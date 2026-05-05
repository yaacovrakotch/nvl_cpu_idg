<#
.SYNOPSIS
    Data-driven MTPL-to-BluePrint generator (v2).

.DESCRIPTION
    Bucket-based compression. For every (TestType, Template, structure) bucket,
    the generator analyses each field (instance name + each parameter) across
    the bucket. Constant fields stay literal in the BP. Varying fields are
    decomposed into longest-common-prefix + symbol + longest-common-suffix and
    represented in the BP with a \SLOT\ placeholder. Per-test symbol values
    are written to <module>.symbols.csv.

    Slot names use the bp-config.json vocabulary (FREQ_CORNER, MODULE_INDEX, ...)
    when the value set matches; otherwise an auto-name `B<id>_<field>` is used.

    Outputs:
      <module>_bp.mtpl           - compressed test programme (non-compilable; hidden during build)
      <module>.symbols.csv      - per-bucket per-test slot value table
      <module>.compressions.log - human-readable bucket tables
      <module>.prompt.txt       - expansion prompt
.PARAMETER InputMtpl
    Source .mtpl file.
.PARAMETER ConfigFile
    bp-config.json (used only for vocabulary hints + notes + copyTargets).
.PARAMETER OutputDir
    Output directory (default: BluePrint/ next to input).
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)] [string]$InputMtpl,
    [Parameter(Mandatory)] [string]$ConfigFile,
    [string]$OutputDir,
    # When true (default) the BP file omits buckets that have no extracted
    # symbols (no Fields and no consolidations) - i.e. verbatim emission only.
    # Set to $false to keep every bucket (round-trip / Expand parity mode).
    [bool]$SymbolizedOnly = $true
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

#region paths
$InputMtpl  = (Resolve-Path $InputMtpl).Path
$ConfigFile = (Resolve-Path $ConfigFile).Path
$moduleName = [IO.Path]::GetFileNameWithoutExtension($InputMtpl)
if (-not $OutputDir) { $OutputDir = Join-Path (Split-Path $InputMtpl) 'BluePrint' }
if (-not (Test-Path $OutputDir)) { New-Item -ItemType Directory $OutputDir -Force | Out-Null }

$bpFile     = Join-Path $OutputDir "${moduleName}_bp.mtpl"
$csvFile    = Join-Path $OutputDir "$moduleName.symbols.csv"
$pivotFile  = Join-Path $OutputDir "$moduleName.symbols.flow_pivot.csv"
$pivotFullFile = Join-Path $OutputDir "$moduleName.symbols.flow_pivot.full.csv"
$logFile    = Join-Path $OutputDir "$moduleName.compressions.log"
$promptFile = Join-Path $OutputDir "$moduleName.prompt.txt"
$derivFile  = Join-Path $OutputDir "$moduleName.derivations.log"

Write-Host "=== MTPL BluePrint Generator (v2 data-driven) ==="
Write-Host "Module : $moduleName"
Write-Host "Input  : $InputMtpl"
Write-Host "Config : $ConfigFile"
Write-Host "Output : $OutputDir"
#endregion

#region restore mtpl from mtpl_orig
$moduleDir = Split-Path $InputMtpl
$origMtpl  = Join-Path $moduleDir "$moduleName.mtpl_orig"
if (Test-Path $origMtpl) {
    Copy-Item -Path $origMtpl -Destination $InputMtpl -Force
    Write-Host "Restored: $InputMtpl from $origMtpl"
} else {
    Copy-Item -Path $InputMtpl -Destination $origMtpl -Force
    Write-Host "First run: saved $origMtpl from current .mtpl"
}
#endregion

#region load config (vocab hints + notes)
$config = Get-Content -Raw $ConfigFile | ConvertFrom-Json
$vocab  = [ordered]@{}
if ($config.PSObject.Properties['symbols']) {
    foreach ($s in $config.symbols) {
        $vocab[$s.name] = @($s.values | ForEach-Object { ($_ -replace '\s*\(.*\)', '').Trim() })
    }
}
$notes = @()
if ($config.PSObject.Properties['notes']) { $notes = @($config.notes) }
Write-Host "  Vocabulary symbols: $($vocab.Count)"
#endregion

#region parse mtpl into preamble + tests + flows
$rawLines = [IO.File]::ReadAllLines($InputMtpl)
Write-Host "  Lines: $($rawLines.Count)"

function Find-EndOfCounters {
    param([string[]]$Lines)
    for ($i = 0; $i -lt $Lines.Count; $i++) {
        if ($Lines[$i] -match '^\}\s*#\s*End of Test Counter Definition') { return $i }
    }
    for ($i = 0; $i -lt $Lines.Count; $i++) {
        if ($Lines[$i] -match '^\s*(CSharpTest|MultiTrialTest)\s+') { return $i - 1 }
    }
    return 0
}

function Parse-BlockBody {
    param([string[]]$Lines, [int]$StartIdx)
    $depth = 0; $opened = $false
    $out = [System.Collections.Generic.List[string]]::new()
    $j = $StartIdx
    while ($j -lt $Lines.Count) {
        $out.Add($Lines[$j])
        $depth += ([regex]::Matches($Lines[$j], '\{')).Count
        $depth -= ([regex]::Matches($Lines[$j], '\}')).Count
        if ($depth -gt 0) { $opened = $true }
        if ($opened -and $depth -le 0) { return @{ Lines = $out; EndIdx = $j } }
        $j++
    }
    return @{ Lines = $out; EndIdx = $j - 1 }
}

function Normalize-BinCounterLine {
    # Replace per-instance bin / counter / baseNumber / BypassPort values with
    # a single canonical token so blocks that differ only in those values can
    # merge. Original values are restored at Expand time from the binmap.
    # SetPointsPreInstance / SetPointsPostInstance values are replaced with
    # the literal "DEFAULT" in the BP and restored from the binmap at Expand.
    param([string]$Line)
    $l = $Line
    if ($l -match '^(\s*(?:##EDC##\s*)?SetBin\s+).+?(\s*;\s*)$') {
        return ($Matches[1] + '__BIN__' + $Matches[2])
    }
    if ($l -match '^(\s*(?:##EDC##\s*)?IncrementCounters\s+).+?(\s*;\s*)$') {
        return ($Matches[1] + '__CTR__' + $Matches[2])
    }
    if ($l -match '^(\s*BaseNumbers\s*=\s*)"[^"]*"(\s*;\s*)$') {
        return ($Matches[1] + '"__BNUM__"' + $Matches[2])
    }
    if ($l -match '^(\s*BypassPort\s*=\s*).+?(\s*;\s*)$') {
        return ($Matches[1] + '__BYPASS__' + $Matches[2])
    }
    if ($l -match '^(\s*SetPointsPreInstance\s*=\s*)"[^"]*"(\s*;\s*)$') {
        return ($Matches[1] + '"DEFAULT"' + $Matches[2])
    }
    if ($l -match '^(\s*SetPointsPostInstance\s*=\s*)"[^"]*"(\s*;\s*)$') {
        return ($Matches[1] + '"DEFAULT"' + $Matches[2])
    }
    return $l
}

function Normalize-BodyLines {
    param([System.Collections.Generic.List[string]]$Body)
    $out = [System.Collections.Generic.List[string]]::new()
    foreach ($l in $Body) { [void]$out.Add((Normalize-BinCounterLine -Line $l)) }
    return $out
}

function Extract-BinCtrValues {
    # Return ordered list of original bin/ctr/bnum/bypass *values* (in body order),
    # i.e. exactly the values that Normalize-BinCounterLine replaced with
    # __BIN__/__CTR__/__BNUM__/__BYPASS__ placeholders.
    # SetPointsPreInstance / SetPointsPostInstance are restored from a single
    # global default (see $globalDefaults sidecar).
    param([System.Collections.Generic.List[string]]$Body)
    $out = [System.Collections.Generic.List[string]]::new()
    foreach ($l in $Body) {
        if ($l -match '^\s*(?:##EDC##\s*)?SetBin\s+(.+?)\s*;\s*$') {
            [void]$out.Add($Matches[1])
        } elseif ($l -match '^\s*(?:##EDC##\s*)?IncrementCounters\s+(.+?)\s*;\s*$') {
            [void]$out.Add($Matches[1])
        } elseif ($l -match '^\s*BaseNumbers\s*=\s*"([^"]*)"\s*;\s*$') {
            [void]$out.Add($Matches[1])
        } elseif ($l -match '^\s*BypassPort\s*=\s*(.+?)\s*;\s*$') {
            [void]$out.Add($Matches[1])
        }
    }
    return $out
}

# Pick a single global default value for SetPointsPreInstance and
# SetPointsPostInstance from the first occurrence in the source mtpl. The
# BP file stores the literal "DEFAULT", and Expand restores all instances
# to this single value.
$globalDefaultPre  = $null
$globalDefaultPost = $null
foreach ($_l in $rawLines) {
    if ($null -eq $globalDefaultPre  -and $_l -match '^\s*SetPointsPreInstance\s*=\s*"([^"]*)"\s*;\s*$')  { $globalDefaultPre  = $Matches[1] }
    if ($null -eq $globalDefaultPost -and $_l -match '^\s*SetPointsPostInstance\s*=\s*"([^"]*)"\s*;\s*$') { $globalDefaultPost = $Matches[1] }
    if ($null -ne $globalDefaultPre -and $null -ne $globalDefaultPost) { break }
}

# Per-instance original bin/ctr/bnum values (used to restore real values
# at Expand time so the emitted .mtpl is build-valid).
$binmapTests = [ordered]@{}
$binmapFlows = [ordered]@{}

$countersEnd   = Find-EndOfCounters -Lines $rawLines
$preambleLines = $rawLines[0..$countersEnd]

$testBlocks = [System.Collections.Generic.List[PSCustomObject]]::new()
$flowBlocks = [System.Collections.Generic.List[PSCustomObject]]::new()

$i = $countersEnd + 1
$inFlowSection = $false
while ($i -lt $rawLines.Count) {
    $line = $rawLines[$i]

    # Test block
    if (-not $inFlowSection -and ($line -match '^\s*CSharpTest\s+(\S+)\s+(\S+)' -or $line -match '^\s*MultiTrialTest\s+(\S+)\s*$')) {
        if ($line -match '^\s*CSharpTest\s+(\S+)\s+(\S+)') {
            $tType = 'CSharpTest'; $tmpl = $Matches[1]; $name = $Matches[2].Trim()
        } else {
            $tType = 'MultiTrialTest'; $tmpl = ''; $name = $Matches[1].Trim()
        }
        # Preceding non-blank comment lines
        $cmt = [System.Collections.Generic.List[string]]::new()
        $k = $i - 1
        while ($k -gt $countersEnd -and ($rawLines[$k] -match '^\s*#' -or $rawLines[$k].Trim() -eq '')) {
            if ($rawLines[$k].Trim()) { $cmt.Insert(0, $rawLines[$k]) }
            $k--
        }
        $parsed = Parse-BlockBody -Lines $rawLines -StartIdx $i
        $rawValues = @(Extract-BinCtrValues -Body $parsed.Lines)
        if ($rawValues.Count -gt 0) { $binmapTests[$name] = $rawValues }
        $normBody = Normalize-BodyLines -Body $parsed.Lines
        $testBlocks.Add([PSCustomObject]@{
            TestType     = $tType
            Template     = $tmpl
            Name         = $name
            CommentLines = $cmt
            BodyLines    = $normBody
            StartLine    = $i
            EndLine      = $parsed.EndIdx
        })
        $i = $parsed.EndIdx + 1
        continue
    }

    # Flow block
    if ($line -match '^\s*Flow\s+(\S+)') {
        $inFlowSection = $true
        $name = $Matches[1]
        $cmt = [System.Collections.Generic.List[string]]::new()
        $k = $i - 1
        while ($k -gt $countersEnd -and ($rawLines[$k] -match '^\s*#' -or $rawLines[$k].Trim() -eq '')) {
            if ($rawLines[$k].Trim()) { $cmt.Insert(0, $rawLines[$k]) }
            $k--
        }
        $parsed = Parse-BlockBody -Lines $rawLines -StartIdx $i
        $rawValues = @(Extract-BinCtrValues -Body $parsed.Lines)
        if ($rawValues.Count -gt 0) { $binmapFlows[$name] = $rawValues }
        $normBody = Normalize-BodyLines -Body $parsed.Lines
        $flowBlocks.Add([PSCustomObject]@{
            Name         = $name
            CommentLines = $cmt
            BodyLines    = $normBody
            StartLine    = $i
            EndLine      = $parsed.EndIdx
        })
        $i = $parsed.EndIdx + 1
        continue
    }

    $i++
}

Write-Host "  Test blocks: $($testBlocks.Count)"
Write-Host "  Flow blocks: $($flowBlocks.Count)"

# --- Drop pre-existing orphan flows. A flow is dropped only if it is NOT
# reachable from any "root" flow, where a root is any flow that nothing else
# refers to via FlowItem (= an entry point, possibly called from outside the
# module). All flows reachable transitively from any root are kept.
# A FlowItem line has the form:
#     [DUT]FlowItem <instanceName> <referencedFlowOrTest> [@flags...]
# Both tokens are treated as references (instanceName usually equals the
# flow name in this codebase, and the 2nd token is the referenced flow/test).
$flowNameSet = New-Object 'System.Collections.Generic.HashSet[string]'
foreach ($fb in $flowBlocks) { [void]$flowNameSet.Add($fb.Name) }

# Per-flow outgoing refs (only refs to other flows in this module).
$flowEdges = @{}
foreach ($fb in $flowBlocks) {
    $outs = New-Object 'System.Collections.Generic.HashSet[string]'
    foreach ($ln in $fb.BodyLines) {
        if ($ln -match '^\s*(?:DUTFlowItem|FlowItem)\s+(\S+)(?:\s+(\S+))?') {
            foreach ($t in @($Matches[1], $Matches[2])) {
                if ($t -and $flowNameSet.Contains($t) -and $t -ne $fb.Name) {
                    [void]$outs.Add($t)
                }
            }
        }
    }
    $flowEdges[$fb.Name] = $outs
}
# Anyone referenced by some other flow.
$referencedSet = New-Object 'System.Collections.Generic.HashSet[string]'
foreach ($outs in $flowEdges.Values) { foreach ($t in $outs) { [void]$referencedSet.Add($t) } }
# Roots = flows not referenced by anything (entry points / called externally).
$roots = New-Object 'System.Collections.Generic.List[string]'
foreach ($fb in $flowBlocks) {
    if (-not $referencedSet.Contains($fb.Name)) { [void]$roots.Add($fb.Name) }
}
# Always keep the very first declared flow as a root, even if (theoretically)
# something else also refers to it -- defensive fallback.
if ($flowBlocks.Count -gt 0 -and -not $roots.Contains($flowBlocks[0].Name)) {
    [void]$roots.Add($flowBlocks[0].Name)
}
# BFS from all roots to find every reachable flow.
$reachable = New-Object 'System.Collections.Generic.HashSet[string]'
$queue = New-Object 'System.Collections.Generic.Queue[string]'
foreach ($r in $roots) { [void]$reachable.Add($r); $queue.Enqueue($r) }
while ($queue.Count -gt 0) {
    $cur = $queue.Dequeue()
    if ($flowEdges.ContainsKey($cur)) {
        foreach ($n in $flowEdges[$cur]) {
            if (-not $reachable.Contains($n)) { [void]$reachable.Add($n); $queue.Enqueue($n) }
        }
    }
}
$keptFlows    = [System.Collections.Generic.List[PSCustomObject]]::new()
$droppedFlows = [System.Collections.Generic.List[string]]::new()
foreach ($fb in $flowBlocks) {
    if ($reachable.Contains($fb.Name)) {
        [void]$keptFlows.Add($fb)
    } else {
        [void]$droppedFlows.Add($fb.Name)
    }
}
if ($droppedFlows.Count -gt 0) {
    Write-Host "  Dropped $($droppedFlows.Count) orphan flow(s) (unreachable from any root in mtpl_orig):" -ForegroundColor Yellow
    foreach ($n in ($droppedFlows | Select-Object -First 20)) { Write-Host "    - $n" -ForegroundColor Yellow }
    if ($droppedFlows.Count -gt 20) { Write-Host "    ...and $($droppedFlows.Count - 20) more" -ForegroundColor Yellow }
    $flowBlocks = $keptFlows
    Write-Host "  Flow blocks (after orphan drop): $($flowBlocks.Count)"
} else {
    Write-Host "  Roots: $($roots.Count); all flows reachable (no orphans dropped)"
}
#endregion

#region helper functions
function Parse-Params {
    # Returns ordered list of @{ LineIdx; Name; Value; Quoted } - any
    # `name = ...;` assignment line (quoted strings OR bare expressions).
    param([System.Collections.Generic.List[string]]$Lines)
    $out = [System.Collections.Generic.List[hashtable]]::new()
    for ($idx = 0; $idx -lt $Lines.Count; $idx++) {
        $l = $Lines[$idx]
        if ($l -match '^\s*#') { continue }
        if ($l -match '^\s*(\w+)\s*=\s*"([^"]*)"\s*;?\s*$') {
            $out.Add(@{ LineIdx = $idx; Name = $Matches[1]; Value = $Matches[2]; Quoted = $true })
        } elseif ($l -match '^\s*(\w+)\s*=\s*(.+?)\s*;\s*$') {
            $out.Add(@{ LineIdx = $idx; Name = $Matches[1]; Value = $Matches[2]; Quoted = $false })
        }
    }
    return $out
}

function Common-Prefix {
    param([string[]]$Strs)
    if (-not $Strs -or $Strs.Count -eq 0) { return '' }
    $p = $Strs[0]
    for ($i = 1; $i -lt $Strs.Count; $i++) {
        $s = $Strs[$i]
        $maxLen = [Math]::Min($p.Length, $s.Length)
        $j = 0
        while ($j -lt $maxLen -and $p[$j] -ceq $s[$j]) { $j++ }
        $p = $p.Substring(0, $j)
        if ($p.Length -eq 0) { return '' }
    }
    return $p
}

function Common-Suffix {
    param([string[]]$Strs)
    if (-not $Strs -or $Strs.Count -eq 0) { return '' }
    $rev = foreach ($s in $Strs) {
        $arr = $s.ToCharArray(); [Array]::Reverse($arr); -join $arr
    }
    $rp = Common-Prefix -Strs @($rev)
    $arr = $rp.ToCharArray(); [Array]::Reverse($arr)
    return -join $arr
}

function Find-VocabName {
    param([string[]]$UniqueValues, [System.Collections.Specialized.OrderedDictionary]$Vocab)
    foreach ($entry in $Vocab.GetEnumerator()) {
        $vSet = [System.Collections.Generic.HashSet[string]]::new([string[]]@($entry.Value), [System.StringComparer]::OrdinalIgnoreCase)
        $isSubset = $true
        foreach ($v in $UniqueValues) {
            if (-not $vSet.Contains($v)) { $isSubset = $false; break }
        }
        if ($isSubset) { return $entry.Key }
    }
    return $null
}

function Get-StructureSignature {
    # Test bucket signature: TestType + Template + comment shape + body structure
    # (param-name list AND non-param body lines verbatim, EXCEPT Flow header /
    # FlowItem identifier names which are abstracted so structurally identical
    # flow blocks merge into a single bucket regardless of the test names they
    # reference). Field decomposition then extracts the varying name parts.
    # NOTE: param ORDER is part of the signature -- Expand emits one body per
    # bucket using test 0's line layout, so tests with the same params in a
    # different order cannot share a bucket without losing original line
    # ordering.
    param($Block)
    $params = Parse-Params -Lines $Block.BodyLines
    $paramKey = ($params | ForEach-Object { $_.Name }) -join '|'
    $cmtKey = ($Block.CommentLines | ForEach-Object { ($_ -replace '\s+', ' ').Trim() }) -join '||'
    $nonParam = [System.Collections.Generic.List[string]]::new()
    for ($i = 0; $i -lt $Block.BodyLines.Count; $i++) {
        # Aggressive whitespace normalization: collapse all runs of whitespace
        # to a single space and trim, so number-of-spaces never affects the
        # bucket signature. The actual emitted .bp body still uses test 0's
        # verbatim line layout.
        $l = (($Block.BodyLines[$i] -replace '\s+', ' ').Trim())
        if ($l -match '^(\w+ = )"[^"]*" ?;?$') {
            $nonParam.Add("<PQ:$($Matches[1])>")
        } elseif ($l -match '^(\w+ = ).+? ?;$') {
            $nonParam.Add("<PU:$($Matches[1])>")
        } elseif ($l -match '^(CSharpTest|MultiTrialTest) ') {
            $nonParam.Add('<H>')
        } elseif ($l -match '^(Flow|DUTFlow) \S+') {
            $nonParam.Add('<FH>')
        } elseif ($l -match '^(FlowItem|DUTFlowItem) \S+') {
            # Strip identifier names; keep flag tokens (@EDC etc.) so flows
            # with vs without flags do NOT merge.
            $flags = ''
            foreach ($m in [regex]::Matches($l, '@\w+')) { $flags += $m.Value }
            $nonParam.Add("<FI$flags>")
        } else {
            $nonParam.Add($l)
        }
    }
    $structKey = $nonParam -join '||'
    $nameShape = ''
    foreach ($ch in $Block.Name.ToCharArray()) {
        if ($ch -eq '_' -or $ch -eq ',') { $nameShape += $ch }
    }
    return "$($Block.TestType)|$($Block.Template)|$paramKey|$cmtKey|$structKey|$nameShape"
}

function Apply-MinMaxRescue {
    # Post-decomposition rescue: when a field's symbol values are exactly the
    # set {"IN","AX"} (in any per-row mix) and the prefix ends with the
    # letter 'M', rotate the trailing 'M' from prefix into each symbol so the
    # values become {"MIN","MAX"} -- much more meaningful in BP / symbols.csv.
    param([hashtable]$Field)
    if (-not $Field) { return }
    if (-not $Field.ContainsKey('SymValues') -or $null -eq $Field.SymValues) { return }
    $vals = @($Field.SymValues)
    if ($vals.Count -eq 0) { return }
    $uniq = @($vals | Sort-Object -Unique)
    if ($uniq.Count -ne 2) { return }
    if (-not (($uniq -contains 'IN') -and ($uniq -contains 'AX'))) { return }
    if (-not $Field.ContainsKey('Prefix') -or $null -eq $Field.Prefix) { return }
    if ($Field.Prefix.Length -lt 1 -or $Field.Prefix[$Field.Prefix.Length - 1] -ne 'M') { return }
    $Field.Prefix = $Field.Prefix.Substring(0, $Field.Prefix.Length - 1)
    $newVals = @($vals | ForEach-Object { 'M' + $_ })
    $Field.SymValues = $newVals
}

function CsvEscape {
    param([string]$s)
    if ($null -eq $s) { return '' }
    if ($s -match '[",\r\n]') { return '"' + ($s -replace '"','""') + '"' }
    return $s
}

function Compact-Whitespace {
    # Collapse internal runs of spaces/tabs to a single space and strip
    # trailing whitespace. Preserves at most ONE leading space when the line
    # had any indentation, so visual nesting is still hinted at without
    # carrying multi-space indent variations into the BP body.
    param([string]$Line)
    if ($null -eq $Line -or $Line.Length -eq 0) { return $Line }
    $hadIndent = ($Line -match '^[ \t]')
    $s = ($Line -replace '[ \t]+', ' ').TrimEnd()
    if (-not $hadIndent -and $s.StartsWith(' ')) { $s = $s.Substring(1) }
    if ($hadIndent -and -not $s.StartsWith(' ')) { $s = ' ' + $s }
    return $s
}

function Write-FileWithRetry {
    # Writes text content to a file even if another process briefly holds a
    # lock (e.g. an editor with the file open). Throws if the file cannot be
    # written -- the BP and the symbols.csv MUST stay in sync, so a silent
    # .new sidecar is not acceptable (the expander would read a stale file).
    param([string]$Path, [string]$Content, [int]$Retries = 8)
    for ($k = 1; $k -le $Retries; $k++) {
        try {
            [IO.File]::WriteAllText($Path, $Content)
            return
        } catch [IO.IOException] {
            if ($k -eq $Retries) { break }
            Start-Sleep -Milliseconds (200 * $k)
        }
    }
    # Last resort: write via .new + Move-Item (atomic on same volume).
    $tmp = "$Path.new"
    [IO.File]::WriteAllText($tmp, $Content)
    for ($k = 1; $k -le $Retries; $k++) {
        try {
            Move-Item -LiteralPath $tmp -Destination $Path -Force -ErrorAction Stop
            return
        } catch {
            if ($k -eq $Retries) {
                try { Remove-Item -LiteralPath $tmp -Force -ErrorAction SilentlyContinue } catch {}
                throw "Cannot write '$Path' -- the file is locked by another process (close any editor/viewer that has it open). BP and symbols.csv must be regenerated together; aborting to avoid stale-pair output."
            }
            Start-Sleep -Milliseconds (300 * $k)
        }
    }
}

function Decompose-OnSeparators {
    # Token-level decomposition. Splits each value on '_' / ',' separators.
    # If all values share the same separator-shape (same separators at the same
    # positions), returns an ordered list of segments
    #   @{ Type='lit'; Text=... }
    #   @{ Type='slot'; SymValues=@(...); SlotName=$null }
    # Adjacent equal tokens become literals; differing tokens become slots that
    # carry the FULL token text (no char-level prefix/suffix slicing).
    # Returns $null when shapes do not match or when there is nothing to vary.
    param([string[]]$Values)
    if (-not $Values -or $Values.Count -eq 0) { return $null }
    $sepChars = @('_', ',')
    $partsList = New-Object System.Collections.Generic.List[hashtable]
    $shape = $null
    foreach ($v in $Values) {
        $words = New-Object System.Collections.Generic.List[string]
        $seps  = New-Object System.Collections.Generic.List[string]
        $cur = ''
        foreach ($ch in $v.ToCharArray()) {
            if ($sepChars -contains $ch) {
                [void]$words.Add($cur); [void]$seps.Add([string]$ch); $cur = ''
            } else { $cur += $ch }
        }
        [void]$words.Add($cur)
        $thisShape = -join $seps
        if ($null -eq $shape) { $shape = $thisShape }
        elseif ($shape -ne $thisShape) { return $null }
        [void]$partsList.Add(@{ Words = $words; Seps = $seps })
    }
    $nWords = $partsList[0].Words.Count
    if ($nWords -le 1) { return $null }   # no separators in any value
    $segs = New-Object System.Collections.Generic.List[hashtable]
    for ($i = 0; $i -lt $nWords; $i++) {
        $col = New-Object System.Collections.Generic.List[string]
        foreach ($p in $partsList) { [void]$col.Add($p.Words[$i]) }
        $arr = $col.ToArray()
        $uniq = @($arr | Sort-Object -Unique)
        if ($uniq.Count -le 1) {
            if ($arr[0]) { [void]$segs.Add(@{ Type='lit'; Text = $arr[0] }) }
        } else {
            [void]$segs.Add(@{ Type='slot'; SymValues = @($arr); SlotName = $null })
        }
        if ($i -lt $nWords - 1) {
            [void]$segs.Add(@{ Type='lit'; Text = $partsList[0].Seps[$i] })
        }
    }
    # Merge adjacent literals
    $merged = New-Object System.Collections.Generic.List[hashtable]
    foreach ($s in $segs) {
        if ($merged.Count -gt 0 -and $merged[$merged.Count-1].Type -eq 'lit' -and $s.Type -eq 'lit') {
            $merged[$merged.Count-1].Text = $merged[$merged.Count-1].Text + $s.Text
        } else { [void]$merged.Add($s) }
    }
    # No slot at all means nothing varies -> caller handles
    $hasSlot = $false
    foreach ($s in $merged) { if ($s.Type -eq 'slot') { $hasSlot = $true; break } }
    if (-not $hasSlot) { return $null }
    return $merged
}

function Tokenize-OnSeps {
    # Split $s into a list of @{ Word; Sep } where Sep is the separator that
    # follows the word ('' for the last token). Separators are '_' or ','.
    param([string]$s)
    $out = New-Object System.Collections.Generic.List[hashtable]
    $cur = ''
    foreach ($ch in $s.ToCharArray()) {
        if ($ch -eq '_' -or $ch -eq ',') {
            [void]$out.Add(@{ Word = $cur; Sep = [string]$ch }); $cur = ''
        } else { $cur += $ch }
    }
    [void]$out.Add(@{ Word = $cur; Sep = '' })
    return $out
}

function Decompose-TokenPrefixSuffix {
    # Fallback when full token shapes do not match: peel off the longest
    # leading run of (word+sep) pairs that are equal across ALL values, and
    # the longest trailing run; everything in the middle becomes a single slot.
    # Returns the segment list, or $null if no token-level commonality.
    param([string[]]$Values)
    if (-not $Values -or $Values.Count -lt 2) { return $null }
    $toks = New-Object System.Collections.Generic.List[object]
    foreach ($v in $Values) { [void]$toks.Add(@(Tokenize-OnSeps -s $v)) }
    $minLen = ($toks | ForEach-Object { $_.Count } | Measure-Object -Minimum).Minimum
    if ($minLen -lt 2) { return $null }

    # Common prefix tokens (full word AND sep must match across all values)
    $pre = 0
    while ($pre -lt $minLen - 1) {
        $t0 = [hashtable]$toks[0][$pre]
        $w = $t0.Word; $s = $t0.Sep
        $same = $true
        for ($k = 1; $k -lt $toks.Count; $k++) {
            $tk = [hashtable]$toks[$k][$pre]
            if ($tk.Word -ne $w -or $tk.Sep -ne $s) { $same = $false; break }
        }
        if (-not $same) { break }
        $pre++
    }
    # Common suffix tokens (right-aligned)
    $suf = 0
    while ($pre + $suf -lt $minLen - 1) {
        $t0 = [hashtable]$toks[0][$toks[0].Count - 1 - $suf]
        $w = $t0.Word; $s = $t0.Sep
        $same = $true
        for ($k = 1; $k -lt $toks.Count; $k++) {
            $tk = [hashtable]$toks[$k][$toks[$k].Count - 1 - $suf]
            if ($tk.Word -ne $w -or $tk.Sep -ne $s) { $same = $false; break }
        }
        if (-not $same) { break }
        $suf++
    }
    if ($pre -eq 0 -and $suf -eq 0) { return $null }

    # Build literal prefix string
    $preStr = ''
    for ($i = 0; $i -lt $pre; $i++) {
        $t = [hashtable]$toks[0][$i]
        $preStr += $t.Word + $t.Sep
    }
    # Build literal suffix string (in original order). Include the separator
    # that PRECEDES the first suffix token so it joins correctly with the slot.
    $sufStr = ''
    $sufStartIdx = $toks[0].Count - $suf
    if ($sufStartIdx - 1 -ge 0) {
        $tprev = [hashtable]$toks[0][$sufStartIdx - 1]
        $sufStr = $tprev.Sep
    }
    for ($i = $sufStartIdx; $i -lt $toks[0].Count; $i++) {
        $t = [hashtable]$toks[0][$i]
        $sufStr += $t.Word + $t.Sep
    }

    # Middle slot values per input
    $mids = New-Object System.Collections.Generic.List[string]
    foreach ($t in $toks) {
        $mid = ''
        $endIdx = $t.Count - $suf
        for ($i = $pre; $i -lt $endIdx; $i++) {
            $tx = [hashtable]$t[$i]
            $mid += $tx.Word
            if ($i -lt $endIdx - 1) { $mid += $tx.Sep }
        }
        [void]$mids.Add($mid)
    }
    $uniq = @($mids | Sort-Object -Unique)
    if ($uniq.Count -le 1) { return $null }

    $segs = New-Object System.Collections.Generic.List[hashtable]
    if ($preStr) { [void]$segs.Add(@{ Type='lit'; Text = $preStr }) }
    [void]$segs.Add(@{ Type='slot'; SymValues = @($mids); SlotName = $null })
    if ($sufStr) { [void]$segs.Add(@{ Type='lit'; Text = $sufStr }) }
    return $segs
}

function Build-Field {
    # Build a field hashtable from raw values. Prefer full token-level
    # decomposition (one column per varying token); fall back to token-level
    # prefix/suffix peel; finally fall back to char-level prefix/suffix.
    param([string]$Name, [int]$LineIdx, [string[]]$Values)
    $field = @{
        Field     = $Name
        LineIdx   = $LineIdx
        Prefix    = ''
        Suffix    = ''
        SymValues = @($Values)
    }
    $segs = Decompose-OnSeparators -Values $Values
    if ($null -eq $segs) { $segs = Decompose-TokenPrefixSuffix -Values $Values }
    if ($null -ne $segs) {
        $field.Segments = $segs
        return $field
    }
    # Fallback: char-level prefix/suffix over the full values, then snap
    # prefix/suffix back to the nearest separator boundary (_ , or word?non-word
    # transition) so slot values stay whole tokens (e.g. MIN/MAX, not IN/AX).
    $pre = Common-Prefix -Strs $Values
    $suf = Common-Suffix -Strs $Values
    $minL = ($Values | ForEach-Object { $_.Length } | Measure-Object -Minimum).Minimum
    while ($pre.Length + $suf.Length -gt $minL) {
        if ($suf.Length -ge $pre.Length) { $suf = $suf.Substring(1) } else { $pre = $pre.Substring(0, $pre.Length - 1) }
    }
    # Snap prefix back: shrink until it ends at a separator OR at a non-word/word
    # boundary relative to the next char in any value.
    $isWord = { param($c) $c -match '[A-Za-z0-9]' }
    while ($pre.Length -gt 0) {
        $last = $pre[$pre.Length - 1]
        $nextChars = $Values | ForEach-Object { if ($_.Length -gt $pre.Length) { $_[$pre.Length] } else { '' } }
        $boundaryOk = $false
        if ($last -eq '_' -or $last -eq ',') { $boundaryOk = $true }
        else {
            $lastIsW = (& $isWord $last)
            $allBoundary = $true
            foreach ($nc in $nextChars) {
                if ($nc -eq '') { continue }
                $ncIsW = (& $isWord $nc)
                if ($lastIsW -eq $ncIsW) { $allBoundary = $false; break }
            }
            if ($allBoundary) { $boundaryOk = $true }
        }
        if ($boundaryOk) { break }
        $pre = $pre.Substring(0, $pre.Length - 1)
    }
    # Snap suffix forward: shrink leading chars until it starts at a separator
    # OR at a word/non-word boundary relative to the preceding char in any value.
    while ($suf.Length -gt 0) {
        $first = $suf[0]
        $prevChars = $Values | ForEach-Object {
            $pos = $_.Length - $suf.Length
            if ($pos -gt 0) { $_[$pos - 1] } else { '' }
        }
        $boundaryOk = $false
        if ($first -eq '_' -or $first -eq ',') { $boundaryOk = $true }
        else {
            $firstIsW = (& $isWord $first)
            $allBoundary = $true
            foreach ($pc in $prevChars) {
                if ($pc -eq '') { continue }
                $pcIsW = (& $isWord $pc)
                if ($firstIsW -eq $pcIsW) { $allBoundary = $false; break }
            }
            if ($allBoundary) { $boundaryOk = $true }
        }
        if ($boundaryOk) { break }
        $suf = $suf.Substring(1)
    }
    $sv = $Values | ForEach-Object { $_.Substring($pre.Length, $_.Length - $pre.Length - $suf.Length) }
    $field.Prefix    = $pre
    $field.Suffix    = $suf
    $field.SymValues = @($sv)
    Apply-MinMaxRescue -Field $field
    return $field
}

function Get-FieldSlotSegments {
    # Returns the list of slot segments inside a field. For simple fields this
    # is a single synthetic slot; for composite fields it's the slot segments
    # in their composite Segments list.
    param([hashtable]$Field)
    if ($Field.ContainsKey('Segments') -and $null -ne $Field.Segments) {
        return @($Field.Segments | Where-Object { $_.Type -eq 'slot' })
    }
    return @(@{ Type='slot'; SymValues = $Field.SymValues; SlotName = $null; _Simple = $true })
}

function Render-FieldValue {
    # Render the param value template (without surrounding quotes).
    # Mode 'sym': substitute the SymValue at the given test index.
    # Mode 'placeholder': substitute the \SlotName\ placeholder.
    param([hashtable]$Field, [int]$TestIdx = 0, [ValidateSet('sym','placeholder')][string]$Mode = 'sym')
    if ($Field.ContainsKey('Segments') -and $null -ne $Field.Segments) {
        $sb = [System.Text.StringBuilder]::new()
        foreach ($s in $Field.Segments) {
            if ($s.Type -eq 'lit') {
                [void]$sb.Append($s.Text)
            } else {
                if ($Mode -eq 'sym') { [void]$sb.Append($s.SymValues[$TestIdx]) }
                else                 { [void]$sb.Append("\$($s.SlotName)\") }
            }
        }
        return $sb.ToString()
    }
    $piece = if ($Mode -eq 'sym') { $Field.SymValues[$TestIdx] } else { "\$($Field.SlotName)\" }
    return "$($Field.Prefix)$piece$($Field.Suffix)"
}
#endregion

#region bucket tests by signature
$bucketsMap = [ordered]@{}
foreach ($tb in $testBlocks) {
    $sig = Get-StructureSignature -Block $tb
    if (-not $bucketsMap.Contains($sig)) {
        $bucketsMap[$sig] = [System.Collections.Generic.List[PSCustomObject]]::new()
    }
    $bucketsMap[$sig].Add($tb)
}
Write-Host "  Buckets: $($bucketsMap.Count)"
#endregion

#region analyse each bucket — find varying fields, prefix/suffix, sym values
$bucketInfos = [System.Collections.Generic.List[hashtable]]::new()

function Build-BucketInfo {
    # Build a bucket-info hashtable (Fields + slot names) from a list of tests.
    param([int]$BucketId, [System.Collections.IEnumerable]$Tests, $Vocab)
    $info = @{
        BucketId = $BucketId
        Tests    = $Tests
        Fields   = [System.Collections.Generic.List[hashtable]]::new()
    }

    # Field: instance name
    $names = @($Tests | ForEach-Object { $_.Name })
    $uniqNames = @($names | Sort-Object -Unique)
    if ($uniqNames.Count -gt 1) {
        $nameField = Build-Field -Name '__INSTANCE__' -LineIdx -1 -Values $names
        $info.Fields.Add($nameField)
    }

    # Each parameter (by ORDER in body, identified via LineIdx of test 0)
    $params0 = Parse-Params -Lines $Tests[0].BodyLines
    foreach ($p0 in $params0) {
        $allValues = New-Object System.Collections.Generic.List[string]
        $ok = $true
        foreach ($t in $Tests) {
            $tp = Parse-Params -Lines $t.BodyLines
            $match = $tp | Where-Object { $_.LineIdx -eq $p0.LineIdx -and $_.Name -eq $p0.Name } | Select-Object -First 1
            if (-not $match) { $ok = $false; break }
            $allValues.Add($match.Value)
        }
        if (-not $ok) { continue }
        $uniq = @($allValues | Sort-Object -Unique)
        if ($uniq.Count -le 1) { continue }
        $newField = Build-Field -Name $p0.Name -LineIdx $p0.LineIdx -Values $allValues.ToArray()
        $newField.Quoted = [bool]$p0.Quoted
        $info.Fields.Add($newField)
    }

    # Slot naming
    $usedSlots = @{}
    foreach ($f in $info.Fields) {
        $isInstance = ($f.Field -eq '__INSTANCE__')
        $instBase = "B$($info.BucketId)_INSTANCE"
        $paramBase = $f.Field
        $isComposite = $f.ContainsKey('Segments') -and $null -ne $f.Segments
        if ($isComposite) {
            $slotSegs = @($f.Segments | Where-Object { $_.Type -eq 'slot' })
            $segIdx = 0
            foreach ($ss in $slotSegs) {
                $segIdx++
                $uv = @($ss.SymValues | Sort-Object -Unique)
                $vName = Find-VocabName -UniqueValues $uv -Vocab $Vocab
                if ($vName -and -not $usedSlots.ContainsKey($vName)) {
                    $ss.SlotName = $vName
                    $usedSlots[$vName] = $true
                } else {
                    $base = if ($isInstance) { $instBase } else { $paramBase }
                    $cand = "${base}_P$segIdx"
                    $n = 1
                    while ($usedSlots.ContainsKey($cand)) { $n++; $cand = "${base}_P${segIdx}_$n" }
                    $ss.SlotName = $cand
                    $usedSlots[$cand] = $true
                }
            }
            $f.SlotName = $null
        } else {
            $uv = @($f.SymValues | Sort-Object -Unique)
            $vName = Find-VocabName -UniqueValues $uv -Vocab $Vocab
            if ($vName -and -not $usedSlots.ContainsKey($vName)) {
                $f.SlotName = $vName
                $usedSlots[$vName] = $true
            } else {
                $cand = if ($isInstance) { $instBase } else { $paramBase }
                $n = 1
                while ($usedSlots.ContainsKey($cand)) { $n++; $cand = if ($isInstance) { "${instBase}_$n" } else { "${paramBase}_$n" } }
                $f.SlotName = $cand
                $usedSlots[$cand] = $true
            }
        }
    }
    return $info
}

function Estimate-BucketCost {
    # Rough character cost = BP representative block + CSV table (header + rows).
    param([hashtable]$Info)
    $rep = $Info.Tests[0]
    $bpChars = 0
    foreach ($c in $rep.CommentLines) { $bpChars += $c.Length + 1 }
    foreach ($l in $rep.BodyLines)    { $bpChars += $l.Length + 1 }
    $bpChars += 40   # bucket marker + blank lines
    # CSV: header line + N data rows
    $slotEntries = New-Object System.Collections.Generic.List[hashtable]
    foreach ($f in $Info.Fields) {
        if ($f.ContainsKey('Segments') -and $null -ne $f.Segments) {
            foreach ($s in $f.Segments) {
                if ($s.Type -eq 'slot') { [void]$slotEntries.Add(@{ Name = $s.SlotName; SymValues = $s.SymValues }) }
            }
        } else {
            [void]$slotEntries.Add(@{ Name = $f.SlotName; SymValues = $f.SymValues })
        }
    }
    $hdr = 'InstanceName,' + (@($slotEntries | ForEach-Object { $_.Name }) -join ',')
    $csvChars = $hdr.Length + 1
    for ($ti = 0; $ti -lt $Info.Tests.Count; $ti++) {
        $row = @($Info.Tests[$ti].Name)
        foreach ($e in $slotEntries) { $row += $e.SymValues[$ti] }
        $csvChars += (($row -join ',').Length + 1)
    }
    return $bpChars + $csvChars
}

$bid = 0
foreach ($entry in $bucketsMap.GetEnumerator()) {
    $bid++
    $info = Build-BucketInfo -BucketId $bid -Tests $entry.Value -Vocab $vocab
    $bucketInfos.Add($info)
}

# Optimization pass: merge buckets that share body-shape (TestType + Template +
# param-name list + non-param body lines + comments) when the merged form costs
# fewer total characters. This collapses sub-buckets that were created only
# because their instance-name token-shapes differed.
function Get-MergeKey { param([hashtable]$Info)
    $rep = $Info.Tests[0]
    $params = Parse-Params -Lines $rep.BodyLines
    $paramKey = ($params | ForEach-Object { $_.Name }) -join '|'
    $cmtKey = ($rep.CommentLines | ForEach-Object { ($_ -replace '\s+', ' ').Trim() }) -join '||'
    $nonParam = New-Object System.Collections.Generic.List[string]
    for ($i = 0; $i -lt $rep.BodyLines.Count; $i++) {
        $l = $rep.BodyLines[$i]
        if ($l -match '^(\s*\w+\s*=\s*)"[^"]*"\s*;?\s*$') { [void]$nonParam.Add("<PQ:$($Matches[1])>") }
        elseif ($l -match '^(\s*\w+\s*=\s*).+?\s*;\s*$') { [void]$nonParam.Add("<PU:$($Matches[1])>") }
        elseif ($l -match '^\s*(CSharpTest|MultiTrialTest)\s+') { [void]$nonParam.Add('<H>') }
        else { [void]$nonParam.Add(($l -replace '\s+', ' ').Trim()) }
    }
    return "$($rep.TestType)|$($rep.Template)|$paramKey|$cmtKey|$($nonParam -join '||')"
}

$groups = @{}
for ($k = 0; $k -lt $bucketInfos.Count; $k++) {
    $key = Get-MergeKey -Info $bucketInfos[$k]
    if (-not $groups.ContainsKey($key)) { $groups[$key] = New-Object System.Collections.Generic.List[int] }
    [void]$groups[$key].Add($k)
}

$mergedBuckets = New-Object System.Collections.Generic.List[hashtable]
$dropIdx = @{}
$mergeCount = 0; $mergeSavings = 0
foreach ($key in $groups.Keys) {
    $idxs = $groups[$key]
    if ($idxs.Count -lt 2) { continue }
    # Combine all tests from these buckets and rebuild
    $allTests = New-Object System.Collections.Generic.List[PSCustomObject]
    $oldCost = 0
    foreach ($i in $idxs) {
        foreach ($t in $bucketInfos[$i].Tests) { [void]$allTests.Add($t) }
        $oldCost += Estimate-BucketCost -Info $bucketInfos[$i]
    }
    $merged = Build-BucketInfo -BucketId ($bucketInfos[$idxs[0]].BucketId) -Tests $allTests -Vocab $vocab
    $newCost = Estimate-BucketCost -Info $merged
    if ($newCost -lt $oldCost) {
        $mergeCount += ($idxs.Count - 1)
        $mergeSavings += ($oldCost - $newCost)
        [void]$mergedBuckets.Add($merged)
        foreach ($i in $idxs) { $dropIdx[$i] = $true }
    }
}

if ($mergeCount -gt 0) {
    $kept = New-Object System.Collections.Generic.List[hashtable]
    for ($k = 0; $k -lt $bucketInfos.Count; $k++) {
        if (-not $dropIdx.ContainsKey($k)) { [void]$kept.Add($bucketInfos[$k]) }
    }
    foreach ($mb in $mergedBuckets) { [void]$kept.Add($mb) }
    # Renumber bucket IDs for stable output and rebuild slot names that reference $info.BucketId
    $renumbered = New-Object System.Collections.Generic.List[hashtable]
    $newBid = 0
    foreach ($b in $kept) {
        $newBid++
        $rebuilt = Build-BucketInfo -BucketId $newBid -Tests $b.Tests -Vocab $vocab
        [void]$renumbered.Add($rebuilt)
    }
    $bucketInfos = $renumbered
    Write-Host "  Optimization: merged $mergeCount buckets (saved ~$mergeSavings chars), final buckets=$($bucketInfos.Count)"
}

$totalFields = 0
foreach ($_bi in $bucketInfos) { $totalFields += $_bi.Fields.Count }
Write-Host "  Total varying test fields across buckets: $totalFields"
#endregion

#region bucket flows by structure signature
function Get-FlowSignature {
    param($Flow)
    # Skeleton: replace each token "WORD" or 'WORD' with <T>, identifiers with <I>,
    # numbers with <N>. Then collapse whitespace. Comments included verbatim.
    $sigSb = [System.Text.StringBuilder]::new()
    foreach ($l in $Flow.BodyLines) {
        $s = $l
        $s = $s -replace '"[^"]*"', '<S>'
        $s = $s -replace "'[^']*'", '<S>'
        $s = $s -replace '\b\d+\b', '<N>'
        $s = ($s -replace '\s+', ' ').Trim()
        [void]$sigSb.Append($s).Append('||')
    }
    $cmtKey = ($Flow.CommentLines | ForEach-Object { ($_ -replace '\s+', ' ').Trim() }) -join '||'
    return "$cmtKey##$($sigSb.ToString())"
}

$flowBucketsMap = [ordered]@{}
foreach ($fb in $flowBlocks) {
    $sig = Get-FlowSignature -Flow $fb
    if (-not $flowBucketsMap.Contains($sig)) {
        $flowBucketsMap[$sig] = [System.Collections.Generic.List[PSCustomObject]]::new()
    }
    $flowBucketsMap[$sig].Add($fb)
}
Write-Host "  Flow buckets: $($flowBucketsMap.Count)"

# Per flow bucket: find each varying token across same line index.
# A token is anything between matching quotes OR a bare identifier word.
function Tokenize-FlowLine {
    param([string]$Line)
    # Yield list of @{ Start; Length; Text; Kind } for each replaceable token
    # Kind: 'quoted' (inside ""), 'word' (\w+ outside quotes/comments).
    $tokens = [System.Collections.Generic.List[hashtable]]::new()
    # Quoted strings
    foreach ($m in [regex]::Matches($Line, '"([^"]*)"')) {
        $tokens.Add(@{ Start = $m.Index + 1; Length = $m.Groups[1].Length; Text = $m.Groups[1].Value; Kind = 'quoted' })
    }
    # Bare words (skip if inside a quoted region)
    $quotedRanges = @()
    foreach ($t in $tokens) { $quotedRanges += @{ S = $t.Start; E = $t.Start + $t.Length } }
    foreach ($m in [regex]::Matches($Line, '\b[A-Za-z_][A-Za-z0-9_]*\b')) {
        $inside = $false
        foreach ($r in $quotedRanges) { if ($m.Index -ge $r.S - 1 -and $m.Index -lt $r.E + 1) { $inside = $true; break } }
        if ($inside) { continue }
        $tokens.Add(@{ Start = $m.Index; Length = $m.Length; Text = $m.Value; Kind = 'word' })
    }
    # Sort by Start
    return @($tokens | Sort-Object { $_.Start })
}

function Build-FlowBucketInfo {
    param([int]$BucketId, $Flows, $Vocab)
    $info = @{
        BucketId = $BucketId
        Flows    = $Flows
        Fields   = [System.Collections.Generic.List[hashtable]]::new()
    }

    # Field: flow name
    $names = @($Flows | ForEach-Object { $_.Name })
    if (@($names | Sort-Object -Unique).Count -gt 1) {
        $p = Common-Prefix -Strs $names
        $s = Common-Suffix -Strs $names
        $minL = ($names | ForEach-Object { $_.Length } | Measure-Object -Minimum).Minimum
        while ($p.Length + $s.Length -gt $minL) {
            if ($s.Length -ge $p.Length) { $s = $s.Substring(1) } else { $p = $p.Substring(0, $p.Length - 1) }
        }
        $sv = $names | ForEach-Object { $_.Substring($p.Length, $_.Length - $p.Length - $s.Length) }
        $fnField = @{
            Field     = '__FLOWNAME__'
            LineIdx   = -1
            TokenIdx  = -1
            Prefix    = $p
            Suffix    = $s
            SymValues = @($sv)
        }
        Apply-MinMaxRescue -Field $fnField
        $info.Fields.Add($fnField)
    }

    # Token-level analysis per body line index using flow 0 as template.
    # Skip line 0 (the `Flow <name>` header) — the flow name is already captured
    # by the __FLOWNAME__ field above; tokenizing it again would create a
    # duplicate slot and cause double substitution at expand time.
    $rep = $Flows[0]
    for ($li = 1; $li -lt $rep.BodyLines.Count; $li++) {
        $repTokens = @(Tokenize-FlowLine -Line $rep.BodyLines[$li])
        if ($repTokens.Count -eq 0) { continue }
        for ($tk = 0; $tk -lt $repTokens.Count; $tk++) {
            $t0 = $repTokens[$tk]
            $values = New-Object System.Collections.Generic.List[string]
            $ok = $true
            foreach ($fb in $Flows) {
                if ($li -ge $fb.BodyLines.Count) { $ok = $false; break }
                $tt = @(Tokenize-FlowLine -Line $fb.BodyLines[$li])
                if ($tk -ge $tt.Count) { $ok = $false; break }
                $tx = $tt[$tk]
                if ($tx.Kind -ne $t0.Kind) { $ok = $false; break }
                $values.Add($tx.Text)
            }
            if (-not $ok) { continue }
            $uniq = @($values | Sort-Object -Unique)
            if ($uniq.Count -le 1) { continue }
            $arr = $values.ToArray()
            $pre = Common-Prefix -Strs $arr
            $suf = Common-Suffix -Strs $arr
            $minL = ($arr | ForEach-Object { $_.Length } | Measure-Object -Minimum).Minimum
            while ($pre.Length + $suf.Length -gt $minL) {
                if ($suf.Length -ge $pre.Length) { $suf = $suf.Substring(1) } else { $pre = $pre.Substring(0, $pre.Length - 1) }
            }
            $sv = $arr | ForEach-Object { $_.Substring($pre.Length, $_.Length - $pre.Length - $suf.Length) }
            $tokField = @{
                Field     = "L${li}T${tk}"
                LineIdx   = $li
                TokenIdx  = $tk
                Prefix    = $pre
                Suffix    = $suf
                SymValues = @($sv)
            }
            Apply-MinMaxRescue -Field $tokField
            $info.Fields.Add($tokField)
        }
    }

    # Slot naming: vocab match else F<id>_<field>
    $usedSlots = @{}
    foreach ($f in $info.Fields) {
        $uv = @($f.SymValues | Sort-Object -Unique)
        $vName = Find-VocabName -UniqueValues $uv -Vocab $Vocab
        if ($vName -and -not $usedSlots.ContainsKey($vName)) {
            $f.SlotName = $vName
            $usedSlots[$vName] = $true
        } else {
            $base = if ($f.Field -eq '__FLOWNAME__') { 'FLOWNAME' } else { $f.Field }
            $cand = "F$($info.BucketId)_$base"
            $n = 1
            while ($usedSlots.ContainsKey($cand)) { $n++; $cand = "F$($info.BucketId)_${base}_$n" }
            $f.SlotName = $cand
            $usedSlots[$cand] = $true
        }
    }
    return $info
}

function Align-FlowBodiesNway {
    # N-way line-level alignment via progressive pairwise LCS. Returns an
    # ordered list of column hashtables: @{ Lines = @($l_0, ..., $l_{N-1}) }
    # where $l_i is $null when flow i has no line at this column. Lines are
    # compared by whitespace-collapsed text for LCS; the original (untouched)
    # lines are stored in the result.
    param($Flows)
    $cols = New-Object System.Collections.Generic.List[hashtable]
    if ($Flows.Count -eq 0) { return $cols }
    foreach ($l in $Flows[0].BodyLines) { [void]$cols.Add(@{ Lines = @($l) }) }
    if ($Flows.Count -eq 1) { return $cols }

    # Shape-based equality: two lines are "alignable" iff their non-token
    # skeleton matches (punctuation, whitespace, keywords-as-shape). All word
    # and quoted tokens are replaced by placeholders so e.g.
    #   `Flow ARR_ATOM_CXX_F1XAT` and `Flow ARR_ATOM_CXX_F2XAT`
    # both collapse to `<W> <W>` and align into a single column. The per-token
    # diff in Build-AlignedFlowBucketInfo then captures the per-flow values
    # (and Find-VocabName promotes them to PMUX_INDEX etc.).
    $normFn = {
        param($l)
        if ($null -eq $l) { return '' }
        $s = ($l -replace '\s+', ' ').Trim()
        $s = [regex]::Replace($s, '"[^"]*"', '<Q>')
        $s = [regex]::Replace($s, '\b[A-Za-z_][A-Za-z0-9_]*\b', '<W>')
        return $s
    }

    for ($fi = 1; $fi -lt $Flows.Count; $fi++) {
        $cNorms = @()
        foreach ($c in $cols) {
            $rep = $null
            foreach ($l in $c.Lines) { if ($null -ne $l) { $rep = $l; break } }
            $cNorms += (& $normFn $rep)
        }
        $newLs = @($Flows[$fi].BodyLines)
        $nNorms = @()
        foreach ($l in $newLs) { $nNorms += (& $normFn $l) }

        $m = $cNorms.Count; $n = $nNorms.Count
        $dp = New-Object 'int[,]' ($m + 1), ($n + 1)
        for ($ii = 1; $ii -le $m; $ii++) {
            for ($jj = 1; $jj -le $n; $jj++) {
                if ($cNorms[$ii - 1] -ceq $nNorms[$jj - 1]) {
                    $dp[$ii, $jj] = $dp[($ii - 1), ($jj - 1)] + 1
                } else {
                    $a = $dp[($ii - 1), $jj]; $b = $dp[$ii, ($jj - 1)]
                    $dp[$ii, $jj] = if ($a -ge $b) { $a } else { $b }
                }
            }
        }
        $rev = New-Object System.Collections.Generic.List[hashtable]
        $ii = $m; $jj = $n
        while ($ii -gt 0 -and $jj -gt 0) {
            if ($cNorms[$ii - 1] -ceq $nNorms[$jj - 1]) {
                [void]$rev.Add(@{ Lines = @($cols[$ii - 1].Lines + @($newLs[$jj - 1])) })
                $ii--; $jj--
            } elseif ($dp[($ii - 1), $jj] -ge $dp[$ii, ($jj - 1)]) {
                [void]$rev.Add(@{ Lines = @($cols[$ii - 1].Lines + @($null)) })
                $ii--
            } else {
                $nulls = @(); for ($k = 0; $k -lt $fi; $k++) { $nulls += , $null }
                [void]$rev.Add(@{ Lines = @($nulls + @($newLs[$jj - 1])) })
                $jj--
            }
        }
        while ($ii -gt 0) {
            [void]$rev.Add(@{ Lines = @($cols[$ii - 1].Lines + @($null)) })
            $ii--
        }
        while ($jj -gt 0) {
            $nulls = @(); for ($k = 0; $k -lt $fi; $k++) { $nulls += , $null }
            [void]$rev.Add(@{ Lines = @($nulls + @($newLs[$jj - 1])) })
            $jj--
        }
        $cols = New-Object System.Collections.Generic.List[hashtable]
        for ($k = $rev.Count - 1; $k -ge 0; $k--) { [void]$cols.Add($rev[$k]) }
    }
    return $cols
}

function Build-AlignedFlowBucketInfo {
    # Build a flow bucket info from N-way LCS-aligned columns. Differs from
    # Build-FlowBucketInfo:
    #   * Body length may differ across flows -- columns where some flows
    #     have a $null line generate a Presence_<col> field (Y/N per flow).
    #   * BP emit reads $info.SyntheticRep.BodyLines instead of Flows[0]; the
    #     synthetic body has one entry per aligned column (first non-null).
    param([int]$BucketId, $Flows, $Vocab)
    $columns = Align-FlowBodiesNway -Flows $Flows

    $synthBody = @()
    foreach ($c in $columns) {
        $rep = $null
        foreach ($l in $c.Lines) { if ($null -ne $l) { $rep = $l; break } }
        $synthBody += $rep
    }

    $rep0 = $Flows[0]
    $synthRep = [PSCustomObject]@{
        Name         = $rep0.Name
        CommentLines = $rep0.CommentLines
        BodyLines    = $synthBody
        StartLine    = $rep0.StartLine
        EndLine      = $rep0.EndLine
    }

    $info = @{
        BucketId     = $BucketId
        Flows        = $Flows
        Fields       = [System.Collections.Generic.List[hashtable]]::new()
        IsAligned    = $true
        SyntheticRep = $synthRep
        Columns      = $columns
    }

    $names = @($Flows | ForEach-Object { $_.Name })
    if (@($names | Sort-Object -Unique).Count -gt 1) {
        $p = Common-Prefix -Strs $names
        $s = Common-Suffix -Strs $names
        $minL = ($names | ForEach-Object { $_.Length } | Measure-Object -Minimum).Minimum
        while ($p.Length + $s.Length -gt $minL) {
            if ($s.Length -ge $p.Length) { $s = $s.Substring(1) } else { $p = $p.Substring(0, $p.Length - 1) }
        }
        $sv = $names | ForEach-Object { $_.Substring($p.Length, $_.Length - $p.Length - $s.Length) }
        $fnField = @{
            Field     = '__FLOWNAME__'
            LineIdx   = -1
            TokenIdx  = -1
            Prefix    = $p
            Suffix    = $s
            SymValues = @($sv)
        }
        Apply-MinMaxRescue -Field $fnField
        $info.Fields.Add($fnField)
    }

    for ($ci = 1; $ci -lt $columns.Count; $ci++) {
        $col = $columns[$ci]
        $allPresent = $true
        foreach ($l in $col.Lines) { if ($null -eq $l) { $allPresent = $false; break } }

        if (-not $allPresent) {
            $sv = @($col.Lines | ForEach-Object { if ($null -eq $_) { 'N' } else { 'Y' } })
            $info.Fields.Add(@{
                Field      = "L${ci}_PRESENCE"
                LineIdx    = $ci
                TokenIdx   = -1
                Prefix     = ''
                Suffix     = ''
                SymValues  = @($sv)
                IsPresence = $true
            })
            continue
        }

        $repTokens = @(Tokenize-FlowLine -Line $col.Lines[0])
        if ($repTokens.Count -eq 0) { continue }
        for ($tk = 0; $tk -lt $repTokens.Count; $tk++) {
            $t0 = $repTokens[$tk]
            $values = New-Object System.Collections.Generic.List[string]
            $ok = $true
            foreach ($ll in $col.Lines) {
                $tt = @(Tokenize-FlowLine -Line $ll)
                if ($tk -ge $tt.Count) { $ok = $false; break }
                $tx = $tt[$tk]
                if ($tx.Kind -ne $t0.Kind) { $ok = $false; break }
                $values.Add($tx.Text)
            }
            if (-not $ok) { continue }
            $uniq = @($values | Sort-Object -Unique)
            if ($uniq.Count -le 1) { continue }
            $arr = $values.ToArray()
            $pre = Common-Prefix -Strs $arr
            $suf = Common-Suffix -Strs $arr
            $minL = ($arr | ForEach-Object { $_.Length } | Measure-Object -Minimum).Minimum
            while ($pre.Length + $suf.Length -gt $minL) {
                if ($suf.Length -ge $pre.Length) { $suf = $suf.Substring(1) } else { $pre = $pre.Substring(0, $pre.Length - 1) }
            }
            $sv = $arr | ForEach-Object { $_.Substring($pre.Length, $_.Length - $pre.Length - $suf.Length) }
            $tokField = @{
                Field     = "L${ci}T${tk}"
                LineIdx   = $ci
                TokenIdx  = $tk
                Prefix    = $pre
                Suffix    = $suf
                SymValues = @($sv)
            }
            Apply-MinMaxRescue -Field $tokField
            $info.Fields.Add($tokField)
        }
    }

    $usedSlots = @{}
    foreach ($f in $info.Fields) {
        $uv = @($f.SymValues | Sort-Object -Unique)
        $vName = Find-VocabName -UniqueValues $uv -Vocab $Vocab
        if ($vName -and -not $usedSlots.ContainsKey($vName)) {
            $f.SlotName = $vName
            $usedSlots[$vName] = $true
        } else {
            $base = if ($f.Field -eq '__FLOWNAME__') { 'FLOWNAME' } else { $f.Field }
            $cand = "F$($info.BucketId)_$base"
            $n = 1
            while ($usedSlots.ContainsKey($cand)) { $n++; $cand = "F$($info.BucketId)_${base}_$n" }
            $f.SlotName = $cand
            $usedSlots[$cand] = $true
        }
    }
    return $info
}

function Estimate-FlowBucketCost {
    param([hashtable]$Info)
    $rep = $Info.Flows[0]
    $bp = 0
    foreach ($l in $rep.CommentLines) { $bp += $l.Length + 1 }
    foreach ($l in $rep.BodyLines)    { $bp += $l.Length + 1 }
    foreach ($f in $Info.Fields) {
        $segLen = ($f.SlotName.Length + 2)
        $origLen = if (@($f.SymValues).Count -gt 0) { $f.SymValues[0].Length } else { 0 }
        $bp += ($segLen - $origLen)
    }
    $bp += 60  # header
    $cols = @($Info.Fields | ForEach-Object { $_.SlotName })
    $hdrRow = (@('FlowName') + $cols) -join ','
    $csv = $hdrRow.Length + 60
    for ($i = 0; $i -lt $Info.Flows.Count; $i++) {
        $row = @($Info.Flows[$i].Name)
        foreach ($f in $Info.Fields) { $row += $f.SymValues[$i] }
        $csv += (($row -join ',').Length + 1)
    }
    return $bp + $csv
}

function Get-FlowMergeKey {
    param($Flow)
    # Looser than Get-FlowSignature: also collapse identifiers to <I> so flows
    # differing only in identifier values can be considered for merging.
    # Counter / bin / baseNumber lines are also collapsed to a generic marker
    # so flows differing only in their bin/counter names still group together.
    $sigSb = [System.Text.StringBuilder]::new()
    foreach ($l in $Flow.BodyLines) {
        $s = $l
        # Collapse SetBin / IncrementCounters / baseNumber-bearing lines first
        if ($s -match '^\s*SetBin\s+') { [void]$sigSb.Append('<BIN_LINE>||'); continue }
        if ($s -match '^\s*IncrementCounters\s+') { [void]$sigSb.Append('<CTR_LINE>||'); continue }
        if ($s -match '\bbaseNumber\b' -or $s -match '\bBaseNumber\b') { [void]$sigSb.Append('<BNUM_LINE>||'); continue }
        $s = $s -replace '"[^"]*"', '<S>'
        $s = $s -replace "'[^']*'", '<S>'
        $s = $s -replace '\b\d+\b', '<N>'
        $s = $s -replace '\b[A-Za-z_][A-Za-z0-9_]*\b', '<I>'
        $s = ($s -replace '\s+', ' ').Trim()
        [void]$sigSb.Append($s).Append('||')
    }
    $cmtKey = ($Flow.CommentLines | ForEach-Object { ($_ -replace '\s+', ' ').Trim() }) -join '||'
    return "$cmtKey##$($sigSb.ToString())"
}

$flowBucketInfos = [System.Collections.Generic.List[hashtable]]::new()
$fid = 0
foreach ($entry in $flowBucketsMap.GetEnumerator()) {
  try {
    $fid++
    $info = Build-FlowBucketInfo -BucketId $fid -Flows $entry.Value -Vocab $vocab
    $flowBucketInfos.Add($info)
  } catch {
    Write-Host "ERROR at fid=$fid bucket sig=$($entry.Key.Substring(0,[Math]::Min(80,$entry.Key.Length))): $_" -ForegroundColor Red
    Write-Host "Stack: $($_.ScriptStackTrace)" -ForegroundColor Red
    throw
  }
}

# ---- Cost-gated flow merge optimisation ----
$fGroups = @{}
for ($k = 0; $k -lt $flowBucketInfos.Count; $k++) {
    $key = Get-FlowMergeKey -Flow $flowBucketInfos[$k].Flows[0]
    if (-not $fGroups.ContainsKey($key)) { $fGroups[$key] = New-Object System.Collections.Generic.List[int] }
    [void]$fGroups[$key].Add($k)
}
$fMergedBuckets = New-Object System.Collections.Generic.List[hashtable]
$fDropIdx = @{}
$fMergeCount = 0; $fMergeSavings = 0
foreach ($key in $fGroups.Keys) {
    $idxs = $fGroups[$key]
    if ($idxs.Count -lt 2) { continue }
    $allFlows = New-Object System.Collections.Generic.List[PSCustomObject]
    $oldCost = 0
    foreach ($i in $idxs) {
        foreach ($f in $flowBucketInfos[$i].Flows) { [void]$allFlows.Add($f) }
        $oldCost += Estimate-FlowBucketCost -Info $flowBucketInfos[$i]
    }
    try {
        $merged = Build-FlowBucketInfo -BucketId ($flowBucketInfos[$idxs[0]].BucketId) -Flows $allFlows -Vocab $vocab
    } catch { continue }
    $newCost = Estimate-FlowBucketCost -Info $merged
    if ($newCost -lt $oldCost) {
        $fMergeCount += ($idxs.Count - 1)
        $fMergeSavings += ($oldCost - $newCost)
        [void]$fMergedBuckets.Add($merged)
        foreach ($i in $idxs) { $fDropIdx[$i] = $true }
    }
}
if ($fMergeCount -gt 0) {
    $kept = New-Object System.Collections.Generic.List[hashtable]
    for ($k = 0; $k -lt $flowBucketInfos.Count; $k++) {
        if (-not $fDropIdx.ContainsKey($k)) { [void]$kept.Add($flowBucketInfos[$k]) }
    }
    foreach ($mb in $fMergedBuckets) { [void]$kept.Add($mb) }
    $renumbered = New-Object System.Collections.Generic.List[hashtable]
    $newFid = 0
    foreach ($b in $kept) {
        $newFid++
        $rebuilt = Build-FlowBucketInfo -BucketId $newFid -Flows $b.Flows -Vocab $vocab
        [void]$renumbered.Add($rebuilt)
    }
    $flowBucketInfos = $renumbered
    Write-Host "  Optimization: merged $fMergeCount flow buckets (saved ~$fMergeSavings chars), final flow buckets=$($flowBucketInfos.Count)"
}

# ---- Force merge ALL remaining flow buckets into one aligned bucket --------
# When the user explicitly nominates a set of flows for blueprint extraction,
# they expect every flow to appear in the result -- even when the flows are
# not structurally identical. This pass runs AFTER the cost-gated merge: if
# more than one flow bucket survived, we N-way LCS-align all flows and rebuild
# a single aligned bucket. Lines present in only some flows produce Presence
# rows in the pivot CSV. Round-trip Expand is not meaningful for an aligned
# bucket and is suppressed by SymbolizedOnly mode upstream.
if ($flowBucketInfos.Count -gt 1) {
    $allFlows = New-Object 'System.Collections.Generic.List[PSCustomObject]'
    foreach ($b in $flowBucketInfos) {
        foreach ($f in $b.Flows) { [void]$allFlows.Add($f) }
    }
    try {
        $aligned = Build-AlignedFlowBucketInfo -BucketId 1 -Flows $allFlows -Vocab $vocab
        $flowBucketInfos = New-Object System.Collections.Generic.List[hashtable]
        [void]$flowBucketInfos.Add($aligned)
        $presenceCt = @($aligned.Fields | Where-Object { $_.ContainsKey('IsPresence') -and $_.IsPresence }).Count
        Write-Host "  Force-aligned $($allFlows.Count) flow(s) into 1 bucket via N-way LCS ($presenceCt presence row(s))"
    } catch {
        Write-Host "  WARNING: force-align failed ($_); leaving $($flowBucketInfos.Count) flow bucket(s)" -ForegroundColor Yellow
    }
}

$totalFlowFields = 0
foreach ($_fbi in $flowBucketInfos) { $totalFlowFields += $_fbi.Fields.Count }
Write-Host "  Total varying flow fields across buckets: $totalFlowFields"
#endregion

#region phase-2 slot consolidation
# After buckets are finalized, look for symbol relationships within each bucket
# so we can deduce a smaller set of independent symbols. Two cases handled:
#   1. FULL match  : two slots have identical SymValues across all rows.
#                    The second slot becomes an alias of the first.
#   2. SUBSTRING   : slot B's value at every row equals  <prefix>+slotA+<suffix>
#                    with a constant prefix/suffix across all rows. Slot B can
#                    be removed; its placeholder rewrites to <prefix>\A\<suffix>.
#
# Consolidations are stored per-bucket as a list of @{ Alias; Primary; Mode;
# Prefix; Suffix } and applied at BP/CSV/log emit time.

function Get-BucketSlotEntries {
    # Returns list of @{ Name; Values; FieldName } for every slot in the bucket
    # (composite fields are flattened into one entry per slot segment).
    param([hashtable]$Info)
    $out = New-Object System.Collections.Generic.List[hashtable]
    foreach ($f in $Info.Fields) {
        $fieldName = $f.Field
        if ($f.ContainsKey('Segments') -and $null -ne $f.Segments) {
            foreach ($s in $f.Segments) {
                if ($s.Type -eq 'slot') {
                    [void]$out.Add(@{ Name = $s.SlotName; Values = @($s.SymValues); FieldName = $fieldName })
                }
            }
        } else {
            [void]$out.Add(@{ Name = $f.SlotName; Values = @($f.SymValues); FieldName = $fieldName })
        }
    }
    return $out
}

function Find-BucketConsolidations {
    param([hashtable]$Info)
    $slots = @(Get-BucketSlotEntries -Info $Info)
    $absorbed = @{}
    $cons = New-Object System.Collections.Generic.List[hashtable]
    for ($a = 0; $a -lt $slots.Count; $a++) {
        if ($absorbed.ContainsKey($slots[$a].Name)) { continue }
        $av = $slots[$a].Values
        if ($av.Count -eq 0) { continue }
        for ($b = $a + 1; $b -lt $slots.Count; $b++) {
            if ($absorbed.ContainsKey($slots[$b].Name)) { continue }
            $bv = $slots[$b].Values
            if ($bv.Count -ne $av.Count) { continue }
            # 1) full match - safest, always valid.
            $eq = $true
            for ($i = 0; $i -lt $av.Count; $i++) {
                if ($av[$i] -cne $bv[$i]) { $eq = $false; break }
            }
            if ($eq) {
                [void]$cons.Add(@{ Alias = $slots[$b].Name; Primary = $slots[$a].Name; Mode = 'full'; Prefix = ''; Suffix = '' })
                $absorbed[$slots[$b].Name] = $true
                continue
            }
            # 2) substring match: bv[i] = pre + av[i] + suf with the SAME
            # pre/suf at every row. Detected as a candidate; later validated
            # by a per-bucket simulated round-trip and dropped if unsafe.
            $pre = $null; $suf = $null
            $valid = $true
            for ($i = 0; $i -lt $av.Count; $i++) {
                $a1 = [string]$av[$i]; $b1 = [string]$bv[$i]
                if ([string]::IsNullOrEmpty($a1)) { $valid = $false; break }
                $idx = $b1.IndexOf($a1)
                if ($idx -lt 0) { $valid = $false; break }
                $thisPre = $b1.Substring(0, $idx)
                $thisSuf = $b1.Substring($idx + $a1.Length)
                if ($null -eq $pre) { $pre = $thisPre; $suf = $thisSuf }
                elseif ($pre -cne $thisPre -or $suf -cne $thisSuf) { $valid = $false; break }
            }
            if ($valid -and ($pre.Length -gt 0 -or $suf.Length -gt 0)) {
                [void]$cons.Add(@{ Alias = $slots[$b].Name; Primary = $slots[$a].Name; Mode = 'substr'; Prefix = $pre; Suffix = $suf })
                $absorbed[$slots[$b].Name] = $true
            }
        }
    }
    return $cons
}

function Test-BucketConsolidations {
    # Simulates Generate's BP body emit + Expand's row substitution for every
    # row in the bucket, using the supplied $cons list. Returns the subset of
    # $cons that produces an EXACT match against the original test bodies.
    # Any consolidation whose application breaks the round-trip is dropped.
    param([hashtable]$Info, $Cons)
    if (-not $Cons -or $Cons.Count -eq 0) { return @() }
    $rep = $Info.Tests[0]
    $absorbedNames = @{}
    foreach ($c in $Cons) { $absorbedNames[$c.Alias] = $c }

    # Build the BP-shape body for test 0: substitute every field with its
    # placeholder form (\SlotName\) - mirrors the real BP emit logic.
    $tmplBody = [System.Collections.Generic.List[string]]@($rep.BodyLines)
    foreach ($f in $Info.Fields) {
        $oldVal = Render-FieldValue -Field $f -TestIdx 0 -Mode 'sym'
        $newVal = Render-FieldValue -Field $f -TestIdx 0 -Mode 'placeholder'
        if ($f.Field -eq '__INSTANCE__') {
            $tmplBody[0] = $tmplBody[0].Replace($oldVal, $newVal)
        } else {
            $li = $f.LineIdx
            $isQuoted = $true
            if ($f.ContainsKey('Quoted')) { $isQuoted = [bool]$f.Quoted }
            if ($isQuoted) { $tmplBody[$li] = $tmplBody[$li].Replace("`"$oldVal`"", "`"$newVal`"") }
            else           { $tmplBody[$li] = $tmplBody[$li].Replace($oldVal, $newVal) }
        }
    }

    # Apply consolidation rewrites: \Alias\ -> [pre]\Primary\[suf]
    $rewritten = [System.Collections.Generic.List[string]]@($tmplBody)
    for ($bi = 0; $bi -lt $rewritten.Count; $bi++) {
        foreach ($c in $Cons) {
            $rewritten[$bi] = $rewritten[$bi].Replace("\$($c.Alias)\", "$($c.Prefix)\$($c.Primary)\$($c.Suffix)")
        }
    }

    # Build the per-row slot tables (mirrors Get-BucketSlotEntries) - use these
    # for simulated expansion. Drop slots that consolidations absorbed.
    $slotEntries = New-Object System.Collections.Generic.List[hashtable]
    foreach ($f in $Info.Fields) {
        if ($f.ContainsKey('Segments') -and $null -ne $f.Segments) {
            foreach ($s in $f.Segments) {
                if ($s.Type -eq 'slot') { [void]$slotEntries.Add(@{ Name = $s.SlotName; Values = $s.SymValues }) }
            }
        } else {
            [void]$slotEntries.Add(@{ Name = $f.SlotName; Values = $f.SymValues })
        }
    }

    # Validate by simulating expansion for each row.
    $okFlags = @{}
    foreach ($c in $Cons) { $okFlags[$c.Alias] = $true }

    for ($row = 0; $row -lt $Info.Tests.Count; $row++) {
        # Build expected = the REAL test body (after BP-shape rewrite for that
        # specific test - i.e. apply field substitutions for THIS row).
        $expected = [System.Collections.Generic.List[string]]@($Info.Tests[$row].BodyLines)
        # We compare against the simulated expansion of the consolidated
        # template using row $row's values.
        $simulated = [System.Collections.Generic.List[string]]@($rewritten)
        for ($si = 0; $si -lt $simulated.Count; $si++) {
            foreach ($e in $slotEntries) {
                if ($absorbedNames.ContainsKey($e.Name)) { continue }
                $simulated[$si] = $simulated[$si].Replace("\$($e.Name)\", [string]$e.Values[$row])
            }
        }
        # Compare line-by-line. Any mismatch invalidates EVERY consolidation
        # that touched a line whose simulated output differs (we are pessimistic
        # and drop them all on this bucket - safer than guessing which one).
        for ($li = 0; $li -lt [Math]::Min($expected.Count, $simulated.Count); $li++) {
            if ($expected[$li] -cne $simulated[$li]) {
                # Mark as failed and exit early - a single bad row invalidates
                # the whole consolidation set for this bucket; reject and let
                # the caller fall back to unconsolidated emission.
                foreach ($c in $Cons) { $okFlags[$c.Alias] = $false }
                break
            }
        }
    }

    return @($Cons | Where-Object { $okFlags[$_.Alias] })
}

# Build per-bucket consolidation map and a flat global summary.
$consolidationsPerBucket = @{}
$consolidationCount = 0
$consolidationDroppedCount = 0
$fullCount = 0
$substrCount = 0
foreach ($info in $bucketInfos) {
    $candidates = @(Find-BucketConsolidations -Info $info)
    if ($candidates.Count -eq 0) { continue }
    $cons = @(Test-BucketConsolidations -Info $info -Cons $candidates)
    $dropped = $candidates.Count - $cons.Count
    $consolidationDroppedCount += $dropped
    if ($cons.Count -gt 0) {
        $consolidationsPerBucket["B$($info.BucketId)"] = $cons
        $consolidationCount += $cons.Count
        foreach ($c in $cons) {
            if ($c.Mode -eq 'full') { $fullCount++ } else { $substrCount++ }
        }
    }
}
Write-Host "  Phase-2 slot consolidations across buckets: $consolidationCount (full=$fullCount, substr=$substrCount; dropped by self-verify=$consolidationDroppedCount)"

function Get-AbsorbedSlots {
    param([string]$BucketKey)
    if (-not $consolidationsPerBucket.ContainsKey($BucketKey)) { return @{} }
    $h = @{}
    foreach ($c in $consolidationsPerBucket[$BucketKey]) { $h[$c.Alias] = $c }
    return $h
}
#endregion

#region emit BP file
$sb = [System.Text.StringBuilder]::new()
$skippedTestBuckets = 0
$skippedFlowBuckets = 0
foreach ($pl in $preambleLines) { [void]$sb.AppendLine((Compact-Whitespace -Line $pl)) }
[void]$sb.AppendLine('')

foreach ($info in $bucketInfos) {
    $rep = $info.Tests[0]
    $bk = "B$($info.BucketId)"
    $hasCons = $consolidationsPerBucket.ContainsKey($bk) -and $consolidationsPerBucket[$bk].Count -gt 0
    $hasFields = ($info.Fields.Count -gt 0)
    if ($SymbolizedOnly -and -not $hasFields -and -not $hasCons) {
        $skippedTestBuckets++
        continue
    }
    [void]$sb.AppendLine('')
    [void]$sb.AppendLine("# BP_BUCKET: B$($info.BucketId) tests=$($info.Tests.Count)")

    # Build modified body of representative test 0
    $body = [System.Collections.Generic.List[string]]@($rep.BodyLines)

    foreach ($f in $info.Fields) {
        $oldVal = Render-FieldValue -Field $f -TestIdx 0 -Mode 'sym'
        $newVal = Render-FieldValue -Field $f -TestIdx 0 -Mode 'placeholder'
        if ($f.Field -eq '__INSTANCE__') {
            $body[0] = $body[0].Replace($oldVal, $newVal)
        } else {
            $li = $f.LineIdx
            $isQuoted = $true
            if ($f.ContainsKey('Quoted')) { $isQuoted = [bool]$f.Quoted }
            if ($isQuoted) {
                $body[$li] = $body[$li].Replace("`"$oldVal`"", "`"$newVal`"")
            } else {
                $body[$li] = $body[$li].Replace($oldVal, $newVal)
            }
        }
    }

    # Phase-2 consolidations: rewrite \Alias\ -> [pre]\Primary\[suf] in body
    $cons = $null
    if ($consolidationsPerBucket.ContainsKey("B$($info.BucketId)")) {
        $cons = $consolidationsPerBucket["B$($info.BucketId)"]
    }
    if ($cons) {
        for ($bi = 0; $bi -lt $body.Count; $bi++) {
            foreach ($c in $cons) {
                $needle  = "\$($c.Alias)\"
                $replace = "$($c.Prefix)\$($c.Primary)\$($c.Suffix)"
                $body[$bi] = $body[$bi].Replace($needle, $replace)
            }
        }
    }

    foreach ($c in $rep.CommentLines) { [void]$sb.AppendLine((Compact-Whitespace -Line $c)) }
    foreach ($l in $body)             { [void]$sb.AppendLine((Compact-Whitespace -Line $l)) }
}

# Flow buckets � use same compress mechanism (one representative per bucket).
[void]$sb.AppendLine('')
[void]$sb.AppendLine('')
foreach ($info in $flowBucketInfos) {
    $rep = if ($info.ContainsKey('SyntheticRep') -and $info.SyntheticRep) { $info.SyntheticRep } else { $info.Flows[0] }
    if ($SymbolizedOnly -and $info.Fields.Count -eq 0) {
        $skippedFlowBuckets++
        continue
    }
    [void]$sb.AppendLine('')
    [void]$sb.AppendLine("# BP_FLOW_BUCKET: F$($info.BucketId) flows=$($info.Flows.Count)")

    $body = [System.Collections.Generic.List[string]]@($rep.BodyLines)

    # Replace flow name in header (first body line)
    $nameField = $info.Fields | Where-Object { $_.Field -eq '__FLOWNAME__' } | Select-Object -First 1
    if ($nameField) {
        $hdr = $body[0]
        $sym0 = $nameField.SymValues[0]
        $oldName = "$($nameField.Prefix)$sym0$($nameField.Suffix)"
        $newName = "$($nameField.Prefix)\$($nameField.SlotName)\$($nameField.Suffix)"
        $body[0] = $hdr.Replace($oldName, $newName)
    }

    # Replace token-level fields (process per line in REVERSE token order so
    # offsets stay stable when we substitute a token's text in-place).
    # NOTE: Group-Object can't group hashtables by key — group manually.
    $byLineMap = @{}
    foreach ($f in $info.Fields) {
        if ($f.Field -eq '__FLOWNAME__') { continue }
        if ($f.ContainsKey('IsPresence') -and $f.IsPresence) { continue }
        $li = [int]$f.LineIdx
        if (-not $byLineMap.ContainsKey($li)) { $byLineMap[$li] = New-Object System.Collections.Generic.List[hashtable] }
        [void]$byLineMap[$li].Add($f)
    }
    foreach ($li in $byLineMap.Keys) {
        if ($li -lt 0 -or $li -ge $body.Count) { continue }
        $line = $body[$li]
        # For each token in this line (from rightmost to leftmost), do the
        # replacement using the current line state's token positions.
        $sortedFields = @($byLineMap[$li] | Sort-Object -Property @{ Expression = { $_.TokenIdx } } -Descending)
        foreach ($f in $sortedFields) {
            $tokens = Tokenize-FlowLine -Line $line
            if ($f.TokenIdx -ge $tokens.Count) { continue }
            $tok = $tokens[$f.TokenIdx]
            $sym0 = $f.SymValues[0]
            # The token's full text should equal Prefix + sym0 + Suffix
            $expected = "$($f.Prefix)$sym0$($f.Suffix)"
            if ($tok.Text -ne $expected) { continue }
            $repl = "$($f.Prefix)\$($f.SlotName)\$($f.Suffix)"
            $line = $line.Substring(0, $tok.Start) + $repl + $line.Substring($tok.Start + $tok.Length)
        }
        $body[[int]$li] = $line
    }

    foreach ($c in $rep.CommentLines) { [void]$sb.AppendLine((Compact-Whitespace -Line $c)) }
    foreach ($l in $body)             { [void]$sb.AppendLine((Compact-Whitespace -Line $l)) }
}

[IO.File]::WriteAllText($bpFile, $sb.ToString().TrimEnd() + "`r`n")
$bpLineCount = [IO.File]::ReadAllLines($bpFile).Count
Write-Host "  BP written: $bpFile ($bpLineCount lines, was $($rawLines.Count))"
if ($SymbolizedOnly -and ($skippedTestBuckets -gt 0 -or $skippedFlowBuckets -gt 0)) {
    Write-Host "  SymbolizedOnly: skipped $skippedTestBuckets verbatim test bucket(s), $skippedFlowBuckets verbatim flow bucket(s)"
}
#endregion

#region emit symbols.csv (per-bucket tabular)
# Format: each bucket is a separate table.
#   # Bucket B<id>  type=Test  template=<tmpl>  tests=<n>
#   InstanceName,SLOT1,SLOT2,...
#   <name>,<v1>,<v2>,...
#   ...
#   <blank line>
#   # Bucket F<id>  type=Flow  flows=<n>
#   FlowName,SLOT1,...
#   ...
$csvLines = [System.Collections.Generic.List[string]]::new()

foreach ($info in $bucketInfos) {
    $tmpl = $info.Tests[0].Template
    $type = $info.Tests[0].TestType
    $csvLines.Add("# Bucket B$($info.BucketId)  type=$type  template=$tmpl  tests=$($info.Tests.Count)")
    # Expand composite fields into one column per slot segment
    $slotEntries = New-Object System.Collections.Generic.List[hashtable]
    foreach ($f in $info.Fields) {
        if ($f.ContainsKey('Segments') -and $null -ne $f.Segments) {
            foreach ($s in $f.Segments) {
                if ($s.Type -eq 'slot') { [void]$slotEntries.Add(@{ Name = $s.SlotName; SymValues = $s.SymValues }) }
            }
        } else {
            [void]$slotEntries.Add(@{ Name = $f.SlotName; SymValues = $f.SymValues })
        }
    }
    # Drop slots that were absorbed by Phase-2 consolidation.
    $absorbed = Get-AbsorbedSlots -BucketKey "B$($info.BucketId)"
    if ($absorbed.Count -gt 0) {
        $slotEntries = [System.Collections.Generic.List[hashtable]]@($slotEntries | Where-Object { -not $absorbed.ContainsKey($_.Name) })
    }
    $hdr = @('InstanceName') + @($slotEntries | ForEach-Object { $_.Name })
    $csvLines.Add(($hdr | ForEach-Object { CsvEscape $_ }) -join ',')
    for ($ti = 0; $ti -lt $info.Tests.Count; $ti++) {
        $row = @($info.Tests[$ti].Name)
        foreach ($e in $slotEntries) { $row += $e.SymValues[$ti] }
        $csvLines.Add(($row | ForEach-Object { CsvEscape $_ }) -join ',')
    }
    $csvLines.Add('')
}

foreach ($info in $flowBucketInfos) {
    $csvLines.Add("# Bucket F$($info.BucketId)  type=Flow  flows=$($info.Flows.Count)")
    $slots = @($info.Fields | ForEach-Object { $_.SlotName })
    $hdr = @('FlowName') + $slots
    $csvLines.Add(($hdr | ForEach-Object { CsvEscape $_ }) -join ',')
    for ($fi = 0; $fi -lt $info.Flows.Count; $fi++) {
        $row = @($info.Flows[$fi].Name)
        foreach ($f in $info.Fields) { $row += $f.SymValues[$fi] }
        $csvLines.Add(($row | ForEach-Object { CsvEscape $_ }) -join ',')
    }
    $csvLines.Add('')
}

Write-FileWithRetry -Path $csvFile -Content (($csvLines.ToArray() -join "`r`n") + "`r`n")
Write-Host "  CSV written: $csvFile ($($bucketInfos.Count) test buckets, $($flowBucketInfos.Count) flow buckets)"
#endregion

#region emit symbols.flow_pivot.csv (one row per Symbol, one column per flow)
# For each symbol slot we collect its value(s) per flow.
#   Flow-bucket symbols   : SymValues[i] is paired with info.Flows[i].Name.
#   Test-bucket symbols   : value comes from each test instance; tests are
#                           mapped to the flows that reference them via
#                           FlowItem in the (kept) flowBlocks. If a flow has
#                           multiple referenced tests with different values
#                           for the same symbol, all unique values are joined
#                           with ' ; '.
# Column order = declaration order of flowBlocks in the (slice) source.

# Build testName -> ordered list of flowName(s) that reference it.
$testNameSet = New-Object 'System.Collections.Generic.HashSet[string]'
foreach ($tb in $testBlocks) { [void]$testNameSet.Add($tb.Name) }
$testToFlows = @{}
foreach ($fb in $flowBlocks) {
    foreach ($ln in $fb.BodyLines) {
        if ($ln -match '^\s*(?:DUTFlowItem|FlowItem)\s+(\S+)(?:\s+(\S+))?') {
            foreach ($t in @($Matches[1], $Matches[2])) {
                if ($t -and $testNameSet.Contains($t)) {
                    if (-not $testToFlows.ContainsKey($t)) {
                        $testToFlows[$t] = New-Object 'System.Collections.Generic.List[string]'
                    }
                    if (-not $testToFlows[$t].Contains($fb.Name)) {
                        [void]$testToFlows[$t].Add($fb.Name)
                    }
                }
            }
        }
    }
}

# Flow column order: declaration order, only flows that appear in any flow bucket.
$flowsInBuckets = New-Object 'System.Collections.Generic.HashSet[string]'
foreach ($fbi in $flowBucketInfos) {
    foreach ($fl in $fbi.Flows) { [void]$flowsInBuckets.Add($fl.Name) }
}
$flowCols = @($flowBlocks | Where-Object { $flowsInBuckets.Contains($_.Name) } | ForEach-Object { $_.Name })

# symbol name -> @{ FlowName -> ordered unique list of values }
$pivot = [ordered]@{}
function Add-PivotValue {
    param([string]$Sym, [string]$Flow, [string]$Val)
    if ([string]::IsNullOrEmpty($Sym) -or [string]::IsNullOrEmpty($Flow)) { return }
    if (-not $pivot.Contains($Sym)) { $pivot[$Sym] = @{} }
    if (-not $pivot[$Sym].ContainsKey($Flow)) {
        $pivot[$Sym][$Flow] = New-Object 'System.Collections.Generic.List[string]'
    }
    if (-not $pivot[$Sym][$Flow].Contains($Val)) { [void]$pivot[$Sym][$Flow].Add($Val) }
}

# Flow buckets: symbol value indexed directly by flow position.
foreach ($info in $flowBucketInfos) {
    foreach ($f in $info.Fields) {
        for ($i = 0; $i -lt $info.Flows.Count; $i++) {
            Add-PivotValue -Sym $f.SlotName -Flow $info.Flows[$i].Name -Val ([string]$f.SymValues[$i])
        }
    }
}

# Test buckets: per-test values, mapped to flow(s) via testToFlows.
foreach ($info in $bucketInfos) {
    # Expand composite fields into one entry per slot segment (mirrors CSV emit).
    $entries = New-Object System.Collections.Generic.List[hashtable]
    foreach ($f in $info.Fields) {
        if ($f.ContainsKey('Segments') -and $null -ne $f.Segments) {
            foreach ($s in $f.Segments) {
                if ($s.Type -eq 'slot') { [void]$entries.Add(@{ Name = $s.SlotName; SymValues = $s.SymValues }) }
            }
        } else {
            [void]$entries.Add(@{ Name = $f.SlotName; SymValues = $f.SymValues })
        }
    }
    $absorbed = Get-AbsorbedSlots -BucketKey "B$($info.BucketId)"
    if ($absorbed.Count -gt 0) {
        $entries = [System.Collections.Generic.List[hashtable]]@($entries | Where-Object { -not $absorbed.ContainsKey($_.Name) })
    }
    for ($ti = 0; $ti -lt $info.Tests.Count; $ti++) {
        $tname = $info.Tests[$ti].Name
        if (-not $testToFlows.ContainsKey($tname)) { continue }
        foreach ($flowName in $testToFlows[$tname]) {
            foreach ($e in $entries) {
                Add-PivotValue -Sym $e.Name -Flow $flowName -Val ([string]$e.SymValues[$ti])
            }
        }
    }
}

# Emit pivot CSV.
$pivotLines = [System.Collections.Generic.List[string]]::new()
$header = @('Symbol') + @($flowCols | ForEach-Object { "$_-flow" })
$pivotLines.Add(($header | ForEach-Object { CsvEscape $_ }) -join ',')
foreach ($symName in $pivot.Keys) {
    $row = @($symName)
    foreach ($flowName in $flowCols) {
        if ($pivot[$symName].ContainsKey($flowName)) {
            $row += (($pivot[$symName][$flowName]) -join ' ; ')
        } else {
            $row += ''
        }
    }
    $pivotLines.Add(($row | ForEach-Object { CsvEscape $_ }) -join ',')
}
Write-FileWithRetry -Path $pivotFile -Content (($pivotLines.ToArray() -join "`r`n") + "`r`n")
Write-FileWithRetry -Path $pivotFullFile -Content (($pivotLines.ToArray() -join "`r`n") + "`r`n")
Write-Host "  Pivot CSV written: $pivotFile ($($pivot.Count) symbols x $($flowCols.Count) flows)"
Write-Host "  Pivot CSV (full, unreduced) written: $pivotFullFile"
#endregion

#region pivot reduction (cross-symbol templates + constant-across-flows drop)
# Goal: minimize the pivot CSV by:
#   (1) Cross-symbol template derivation. Detect when symbol D's per-flow
#       value can be reproduced as a fixed string template T(B) using another
#       symbol B's per-flow value -- e.g.
#       F2_L3T1=PMUX_INDEX+"XAT_HITO_VCCIA_F"+PMUX_INDEX. When found, rewrite
#       \D\ in BP to the template and drop D from pivot.
#   (2) Constant filter. After (1), drop pivot rows whose populated cells all
#       hold the same value (BP keeps the \X\ placeholder; the value is a
#       global constant for this slice).
#
# Restriction: only single-value (1 value per cell) symbols participate in
# (1) -- multi-value rows have no clean template.

# Build a single-value map: { symbol -> @{ flow -> value } }.
$symValueMap = [ordered]@{}
foreach ($symName in $pivot.Keys) {
    $vals = @{}
    $singleValueOnly = $true
    foreach ($flowName in $flowCols) {
        if ($pivot[$symName].ContainsKey($flowName)) {
            $vlist = $pivot[$symName][$flowName]
            if ($vlist.Count -gt 1) { $singleValueOnly = $false; break }
            $vals[$flowName] = [string]$vlist[0]
        }
    }
    if ($singleValueOnly) { $symValueMap[$symName] = $vals }
}

# Sort by total length of values ascending (shortest = best basis candidate).
$symsByLen = @($symValueMap.Keys | Sort-Object {
    ($symValueMap[$_].Values | Measure-Object -Property Length -Sum).Sum
})

# Helper: extract basis value from a derived value given template parts.
# Returns $null when extraction is ambiguous or fails. Handles parts.Count >= 2
# with a non-empty inner separator (Parts[1..k-1]) for the multi-occurrence
# case; the simple 2-part case always works when prefix/suffix match.
function Try-InverseExtract {
    param([string]$D, [string[]]$Parts)
    if ($Parts.Count -lt 2) { return $null }
    if ($null -eq $D) { return $null }
    $p0 = [string]$Parts[0]
    $pL = [string]$Parts[$Parts.Count - 1]
    if (-not $D.StartsWith($p0)) { return $null }
    if (-not $D.EndsWith($pL))   { return $null }
    if ($D.Length -lt ($p0.Length + $pL.Length)) { return $null }
    $mid = $D.Substring($p0.Length, $D.Length - $p0.Length - $pL.Length)
    if ($Parts.Count -eq 2) { return $mid }
    # mid = B + Parts[1] + B + Parts[2] + ... + Parts[k-1] + B
    # Need an unambiguous inner separator; require all inner parts identical
    # and non-empty so we can split mid.
    $inner = [string]$Parts[1]
    if ([string]::IsNullOrEmpty($inner)) { return $null }
    for ($i = 2; $i -lt $Parts.Count - 1; $i++) {
        if ([string]$Parts[$i] -cne $inner) { return $null }
    }
    $bs = [regex]::Split($mid, [regex]::Escape($inner))
    if ($bs.Count -ne ($Parts.Count - 1)) { return $null }
    $first = $bs[0]
    foreach ($x in $bs) { if ($x -cne $first) { return $null } }
    return $first
}

# Iteratively enrich symValueMap by forward + inverse template fills until
# fixpoint (max 25 iterations as a hard guard). Each iteration:
#   1) Re-derive every (basis, derived) template rule from the CURRENT map.
#   2) Forward-fill: for each rule, set derived[f] = template(basis[f]) when
#      derived[f] is missing and basis[f] exists.
#   3) Inverse-fill: for each rule, set basis[f] from derived[f] when basis is
#      missing and derived has the value (only when extraction is unambiguous).
$enrichedFwd = 0
$enrichedInv = 0
for ($iter = 0; $iter -lt 25; $iter++) {
    $rules = New-Object System.Collections.Generic.List[hashtable]
    foreach ($basis in $symsByLen) {
        $bMap = $symValueMap[$basis]
        foreach ($derived in $symsByLen) {
            if ($derived -eq $basis) { continue }
            $dMap = $symValueMap[$derived]
            $coFlows = @($dMap.Keys | Where-Object { $bMap.ContainsKey($_) })
            if ($coFlows.Count -lt 2) { continue }
            $parts = $null; $valid = $true
            foreach ($f in $coFlows) {
                $b = [string]$bMap[$f]
                $d = [string]$dMap[$f]
                if ([string]::IsNullOrEmpty($b)) { $valid = $false; break }
                if ($d.IndexOf($b) -lt 0)        { $valid = $false; break }
                $cur = [regex]::Split($d, [regex]::Escape($b))
                if ($null -eq $parts) { $parts = $cur; continue }
                if ($cur.Count -ne $parts.Count) { $valid = $false; break }
                for ($pi = 0; $pi -lt $parts.Count; $pi++) {
                    if ([string]$parts[$pi] -cne [string]$cur[$pi]) { $valid = $false; break }
                }
                if (-not $valid) { break }
            }
            if (-not $valid -or $parts.Count -lt 2) { continue }
            [void]$rules.Add(@{ Basis = $basis; Derived = $derived; Parts = $parts })
        }
    }
    $changed = $false
    foreach ($r in $rules) {
        $bMap = $symValueMap[$r.Basis]; $dMap = $symValueMap[$r.Derived]
        # Forward
        foreach ($f in @($bMap.Keys)) {
            if (-not $dMap.ContainsKey($f)) {
                $val = ($r.Parts) -join ([string]$bMap[$f])
                $dMap[$f] = $val
                $enrichedFwd++; $changed = $true
            }
        }
        # Inverse
        foreach ($f in @($dMap.Keys)) {
            if (-not $bMap.ContainsKey($f)) {
                $extracted = Try-InverseExtract -D ([string]$dMap[$f]) -Parts $r.Parts
                if ($null -ne $extracted) {
                    $bMap[$f] = $extracted
                    $enrichedInv++; $changed = $true
                }
            }
        }
    }
    if (-not $changed) { break }
}
if (($enrichedFwd + $enrichedInv) -gt 0) {
    Write-Host "  Pivot enrichment: filled $enrichedFwd forward and $enrichedInv inverse cell(s) via template chains"
    # Push enriched values back into the pivot so missing flow cells are no
    # longer blank in the CSV output.
    foreach ($symName in $symValueMap.Keys) {
        $vals = $symValueMap[$symName]
        if (-not $pivot.Contains($symName)) { $pivot[$symName] = @{} }
        foreach ($f in $vals.Keys) {
            if (-not $pivot[$symName].ContainsKey($f)) {
                $pivot[$symName][$f] = New-Object 'System.Collections.Generic.List[string]'
            }
            if ($pivot[$symName][$f].Count -eq 0) {
                [void]$pivot[$symName][$f].Add([string]$vals[$f])
            }
        }
    }
}

$crossDerivations = [ordered]@{}
$crossAbsorbed = @{}

foreach ($basis in $symsByLen) {
    if ($crossAbsorbed.ContainsKey($basis)) { continue }
    if (-not $symValueMap.Contains($basis)) { continue }
    foreach ($derived in $symsByLen) {
        if ($derived -eq $basis) { continue }
        if ($crossDerivations.Contains($derived)) { continue }
        if ($crossAbsorbed.ContainsKey($derived)) { continue }
        if (-not $symValueMap.Contains($derived)) { continue }

        $bMap = $symValueMap[$basis]; $dMap = $symValueMap[$derived]
        # Basis must cover every flow where derived has a value (so absorption
        # produces the same BP content for every populated row).
        $coFlows = @($dMap.Keys | Sort-Object)
        if ($coFlows.Count -lt 2) { continue }
        $missingInBasis = $false
        foreach ($f in $coFlows) { if (-not $bMap.ContainsKey($f)) { $missingInBasis = $true; break } }
        if ($missingInBasis) { continue }

        $parts = $null
        $valid = $true
        foreach ($f in $coFlows) {
            $b = [string]$bMap[$f]
            $d = [string]$dMap[$f]
            if ([string]::IsNullOrEmpty($b)) { $valid = $false; break }
            if ($d.IndexOf($b) -lt 0)        { $valid = $false; break }
            $cur = [regex]::Split($d, [regex]::Escape($b))
            if ($null -eq $parts) { $parts = $cur; continue }
            if ($cur.Count -ne $parts.Count) { $valid = $false; break }
            for ($pi = 0; $pi -lt $parts.Count; $pi++) {
                if ([string]$parts[$pi] -cne [string]$cur[$pi]) { $valid = $false; break }
            }
            if (-not $valid) { break }
        }
        if (-not $valid -or $parts.Count -lt 2) { continue }

        $crossDerivations[$derived] = @{ Basis = $basis; Parts = $parts }
        $crossAbsorbed[$derived] = $true
    }
}

# Apply derivations to BP file (read -> replace -> write).
if ($crossDerivations.Count -gt 0) {
    $bpContent = [IO.File]::ReadAllText($bpFile)
    foreach ($d in $crossDerivations.Keys) {
        $info = $crossDerivations[$d]
        $repl = $info.Parts -join "\$($info.Basis)\"
        $bpContent = $bpContent.Replace("\$d\", $repl)
        $pivot.Remove($d)
    }
    Write-FileWithRetry -Path $bpFile -Content $bpContent
    Write-Host "  Pivot derivations: $($crossDerivations.Count) symbol(s) absorbed via cross-symbol templates (BP rewritten)"
}

# Multi-value pivot absorption is intentionally disabled: per-test aggregates
# like B13_INSTANCE_P1 / B14_INSTANCE_P1 / ScreenTestSet are referenced by
# the BP via \<slot>\ tokens, so every BP symbol must appear in the symbols
# file. Joined-by-' ; ' multi-value cells are kept in the pivot row.
$multiAbsorbed = 0

# Multi-value template substitution (robust positional aligner). For each
# multi-value pivot row, try every single-value symbol as basis. Tokenize
# every value into alternating word / non-word segments via [regex]::Split
# `(\W+)`, align segment-position-wise across flows, and substitute basis
# only at positions where the variation matches the basis values exactly
# (literal positions like trailing `_1` stay literal). If every value across
# all flows reduces to the SAME templated string, replace the row's cells
# with the templated form (one identical entry per flow).
function _Try-PositionalTemplate {
    param([string[]]$Vals, [string[]]$Basis)
    # $Vals[i] is the value for flow i; $Basis[i] is that flow's basis value.
    # Returns the templated string (with sentinel placeholders) iff every
    # value reduces to the same template AND at least one position used basis.
    if ($Vals.Length -ne $Basis.Length -or $Vals.Length -lt 2) { return $null }
    # Tokenize on underscore + non-word characters (\W excludes _ in .NET regex).
    $tokens = @()
    $count = -1
    foreach ($v in $Vals) {
        $tk = [regex]::Split($v, '([_\W]+)')
        if ($count -lt 0) { $count = $tk.Length }
        elseif ($tk.Length -ne $count) { return $null }
        $tokens += , $tk
    }
    $out = New-Object 'System.Collections.Generic.List[string]'
    $usedBasis = $false
    for ($p = 0; $p -lt $count; $p++) {
        $atP = @()
        for ($i = 0; $i -lt $Vals.Length; $i++) { $atP += $tokens[$i][$p] }
        $first = $atP[0]
        $allEq = $true
        foreach ($t in $atP) { if ($t -cne $first) { $allEq = $false; break } }
        if ($allEq) { [void]$out.Add($first); continue }
        # Variation. Compute common prefix/suffix; the middle must equal basis.
        $minL = ($atP | ForEach-Object { $_.Length } | Measure-Object -Minimum).Minimum
        $pre = ''
        for ($k = 0; $k -lt $minL; $k++) {
            $c = $atP[0][$k]
            $ok = $true
            foreach ($t in $atP) { if ($t[$k] -cne $c) { $ok = $false; break } }
            if (-not $ok) { break }
            $pre += $c
        }
        $suf = ''
        for ($k = 1; $k -le ($minL - $pre.Length); $k++) {
            $c = $atP[0][$atP[0].Length - $k]
            $ok = $true
            foreach ($t in $atP) { if ($t[$t.Length - $k] -cne $c) { $ok = $false; break } }
            if (-not $ok) { break }
            $suf = $c + $suf
        }
        $matchesBasis = $true
        for ($i = 0; $i -lt $Vals.Length; $i++) {
            $mid = $atP[$i].Substring($pre.Length, $atP[$i].Length - $pre.Length - $suf.Length)
            if ($mid -cne $Basis[$i]) { $matchesBasis = $false; break }
        }
        if (-not $matchesBasis) { return $null }
        [void]$out.Add("$pre`u{0001}__BASIS__`u{0001}$suf")
        $usedBasis = $true
    }
    if (-not $usedBasis) { return $null }
    return -join $out
}

$multiTemplated = 0
$exemptFromConstFilter = @{}
foreach ($symName in @($pivot.Keys)) {
    $perFlow = @{}
    $hasMulti = $false
    $valCount = -1
    $consistentCount = $true
    $orderedFlows = New-Object 'System.Collections.Generic.List[string]'
    foreach ($flowName in $flowCols) {
        if (-not $pivot[$symName].ContainsKey($flowName)) { continue }
        $vs = @($pivot[$symName][$flowName])
        if ($vs.Count -gt 1) { $hasMulti = $true }
        if ($valCount -lt 0) { $valCount = $vs.Count }
        elseif ($valCount -ne $vs.Count) { $consistentCount = $false; break }
        $perFlow[$flowName] = $vs
        [void]$orderedFlows.Add($flowName)
    }
    if (-not $hasMulti -or -not $consistentCount) { continue }
    if ($orderedFlows.Count -lt 2) { continue }

    foreach ($basis in $pivot.Keys) {
        if ($basis -eq $symName) { continue }
        $bArr = @()
        $bOk = $true
        foreach ($flowName in $orderedFlows) {
            if (-not $pivot[$basis].ContainsKey($flowName)) { $bOk = $false; break }
            $bv = @($pivot[$basis][$flowName])
            if ($bv.Count -ne 1) { $bOk = $false; break }
            $b1 = [string]$bv[0]
            if ([string]::IsNullOrEmpty($b1)) { $bOk = $false; break }
            $bArr += $b1
        }
        if (-not $bOk) { continue }
        $distinctB = @($bArr | Sort-Object -Unique)
        if ($distinctB.Count -lt $bArr.Length) { continue }

        # For each value-position k, try positional template; collect templates.
        $rendered = New-Object 'System.Collections.Generic.List[string]'
        $allOk = $true
        for ($k = 0; $k -lt $valCount; $k++) {
            $valsAtK = @()
            foreach ($flowName in $orderedFlows) { $valsAtK += [string]$perFlow[$flowName][$k] }
            $tmpl = _Try-PositionalTemplate -Vals $valsAtK -Basis $bArr
            if ($null -eq $tmpl) { $allOk = $false; break }
            [void]$rendered.Add($tmpl.Replace("`u{0001}__BASIS__`u{0001}", "\$basis\"))
        }
        if (-not $allOk) { continue }

        foreach ($flowName in $orderedFlows) {
            $newList = New-Object 'System.Collections.Generic.List[string]'
            foreach ($r in $rendered) { [void]$newList.Add($r) }
            $pivot[$symName][$flowName] = $newList
        }
        $exemptFromConstFilter[$symName] = $true
        $multiTemplated++
        break
    }
}
if ($multiTemplated -gt 0) {
    Write-Host "  Pivot multi-value templating: $multiTemplated symbol(s) rewritten via positional basis substitution"
}

# Inline-constant absorption: any symbol whose populated flow columns all
# produce the same (' ; '-joined) string is redundant in the symbols file.
# Replace its \<sym>\ placeholder in the BP with the literal text and drop
# the row. This applies to multi-value rows just rewritten by templating,
# but also catches any single-value row that already happens to match.
$inlinedConst = 0
$bpInlineContent = $null
foreach ($symName in @($pivot.Keys)) {
    # Only inline single-value-per-flow symbols. Multi-value rows (per-test
    # slots like B13_INSTANCE_P1) keep one placeholder in the BP that the
    # expander iterates per row -- inlining a joined ' ; ' string would
    # collapse all rows into one literal and break expansion.
    $multiValue = $false
    foreach ($flowName in $flowCols) {
        if (-not $pivot[$symName].ContainsKey($flowName)) { continue }
        if (@($pivot[$symName][$flowName]).Count -ne 1) { $multiValue = $true; break }
    }
    if ($multiValue) { continue }
    $popVals = @($flowCols |
        Where-Object { $pivot[$symName].ContainsKey($_) } |
        ForEach-Object { ($pivot[$symName][$_]) -join ' ; ' })
    if ($popVals.Count -lt 1) { continue }
    $first = $popVals[0]
    $allEq = $true
    foreach ($v in $popVals) { if ($v -cne $first) { $allEq = $false; break } }
    if (-not $allEq) { continue }
    if (-not $exemptFromConstFilter.ContainsKey($symName)) { continue }
    if ($null -eq $bpInlineContent) { $bpInlineContent = [IO.File]::ReadAllText($bpFile) }
    $bpInlineContent = $bpInlineContent.Replace("\$symName\", $first)
    [void]$exemptFromConstFilter.Remove($symName)
    $pivot.Remove($symName)
    $inlinedConst++
}
if ($inlinedConst -gt 0) {
    Write-FileWithRetry -Path $bpFile -Content $bpInlineContent
    Write-Host "  Pivot inline-constant: $inlinedConst symbol(s) inlined into BP and dropped from symbols"
}

# Constant-across-flows filter: drop the pivot row only when it's safe --
# i.e. it's NOT a multi-value (per-test) symbol. Multi-value rows must stay
# in the symbols file because their \<sym>\ placeholder in the BP expands
# differently per test row, and the expander reads those values from this
# file. Single-value constant rows would already have been inlined above
# when exempt; any leftover single-value constants are also kept (the BP
# still has a \<sym>\ placeholder for them).
$constDropped = 0
foreach ($symName in @($pivot.Keys)) {
    if ($exemptFromConstFilter.ContainsKey($symName)) { continue }
    # Skip multi-value symbols entirely -- never drop them from the pivot.
    $multiValue = $false
    foreach ($flowName in $flowCols) {
        if (-not $pivot[$symName].ContainsKey($flowName)) { continue }
        if (@($pivot[$symName][$flowName]).Count -ne 1) { $multiValue = $true; break }
    }
    if ($multiValue) { continue }
    $popVals = @($flowCols |
        Where-Object { $pivot[$symName].ContainsKey($_) } |
        ForEach-Object { ($pivot[$symName][$_]) -join ' ; ' })
    if ($popVals.Count -lt 2) { continue }
    $first = $popVals[0]
    $allEq = $true
    foreach ($v in $popVals) { if ($v -cne $first) { $allEq = $false; break } }
    if ($allEq) {
        $pivot.Remove($symName)
        $constDropped++
    }
}
if ($constDropped -gt 0) {
    Write-Host "  Pivot constant-filter: $constDropped symbol(s) dropped (constant across all populated flows)"
}

# Multi-value-constant inlining: any remaining row whose populated flow
# columns all produce the same value list is not really a "symbol" -- it's
# a per-row literal sequence. Emit it into the BP as a per-bucket
# `# CONST: <name> = v0 ; v1 ; ...` annotation immediately after the
# `# BP_BUCKET: ...` header of every bucket whose body references the
# `\<name>\` placeholder. Then drop the row from the pivot. The downstream
# expander can read these CONST lines as per-row literal columns.
$multiConstInlined = 0
$bpForConst = $null
foreach ($symName in @($pivot.Keys)) {
    $valLists = @()
    foreach ($flowName in $flowCols) {
        if (-not $pivot[$symName].ContainsKey($flowName)) { continue }
        $valLists += ,(@($pivot[$symName][$flowName]))
    }
    if ($valLists.Count -lt 1) { continue }
    # Need at least one multi-value entry (single-value constants have
    # already been inlined above).
    $isMulti = $false
    foreach ($vl in $valLists) { if ($vl.Count -gt 1) { $isMulti = $true; break } }
    if (-not $isMulti) { continue }
    # All flow columns must produce the same value list.
    $ref = $valLists[0]
    $allSame = $true
    for ($i = 1; $i -lt $valLists.Count; $i++) {
        $cur = $valLists[$i]
        if ($cur.Count -ne $ref.Count) { $allSame = $false; break }
        for ($k = 0; $k -lt $ref.Count; $k++) {
            if ([string]$cur[$k] -cne [string]$ref[$k]) { $allSame = $false; break }
        }
        if (-not $allSame) { break }
    }
    if (-not $allSame) { continue }

    if ($null -eq $bpForConst) { $bpForConst = [IO.File]::ReadAllLines($bpFile) }
    $needle = "\$symName\"
    # Find every bucket header (test or flow) whose body references the
    # placeholder, and inject a CONST line right after the header.
    $newBp = New-Object 'System.Collections.Generic.List[string]'
    $bucketStart = -1
    $bucketUses = $false
    for ($li = 0; $li -lt $bpForConst.Count; $li++) {
        $bl = $bpForConst[$li]
        $isHeader = ($bl -match '^# BP_BUCKET:' -or $bl -match '^# BP_FLOW_BUCKET:')
        if ($isHeader) {
            # Flush any pending header that needs a CONST insertion done now.
            $bucketStart = $newBp.Count
            $bucketUses = $false
        } elseif ($bucketStart -ge 0 -and (-not $bucketUses) -and $bl.Contains($needle)) {
            $bucketUses = $true
            # Inject CONST line right after the bucket header (which is at
            # $bucketStart in the new list).
            $constLine = "# CONST: $symName = " + (($ref | ForEach-Object { [string]$_ }) -join ' ; ')
            $newBp.Insert($bucketStart + 1, $constLine)
        }
        [void]$newBp.Add($bl)
    }
    $bpForConst = $newBp.ToArray()
    $pivot.Remove($symName)
    $multiConstInlined++
}
if ($multiConstInlined -gt 0) {
    [IO.File]::WriteAllLines($bpFile, $bpForConst)
    Write-Host "  Pivot multi-value-constant inline: $multiConstInlined symbol(s) inlined as # CONST: lines into BP and dropped from symbols"
}

# Re-emit the pivot CSV with the reduced row set.
if ($crossDerivations.Count -gt 0 -or $constDropped -gt 0 -or $multiAbsorbed -gt 0 -or $multiTemplated -gt 0 -or $inlinedConst -gt 0 -or $multiConstInlined -gt 0) {
    $pivotLines = [System.Collections.Generic.List[string]]::new()
    $header = @('Symbol') + @($flowCols | ForEach-Object { "$_-flow" })
    $pivotLines.Add(($header | ForEach-Object { CsvEscape $_ }) -join ',')
    foreach ($symName in $pivot.Keys) {
        $row = @($symName)
        foreach ($flowName in $flowCols) {
            if ($pivot[$symName].ContainsKey($flowName)) {
                $row += (($pivot[$symName][$flowName]) -join ' ; ')
            } else {
                $row += ''
            }
        }
        $pivotLines.Add(($row | ForEach-Object { CsvEscape $_ }) -join ',')
    }
    Write-FileWithRetry -Path $pivotFile -Content (($pivotLines.ToArray() -join "`r`n") + "`r`n")
    Write-Host "  Pivot CSV (reduced) written: $pivotFile ($($pivot.Count) symbols)"

    # The reduced pivot IS the symbols file: a single-table view, one row per
    # BP symbol, one column per flow. Multi-value cells are joined by ' ; '.
    # This guarantees every \<slot>\ token in the BP appears in the symbols
    # file (no separate per-bucket sections to chase).
    Write-FileWithRetry -Path $csvFile -Content (($pivotLines.ToArray() -join "`r`n") + "`r`n")
    Write-Host "  Symbols CSV (single-table) re-written: $csvFile ($($pivot.Count) symbols)"
}

# Coherence check: every \<sym>\ placeholder in the final BP must be
# resolvable from EITHER (a) a row in the symbols.csv pivot, OR (b) a
# `# CONST: <sym> = ...` annotation inside one of the buckets that
# references it. Reserved tokens like __BYPASS__ / __BIN__ are not symbols
# and use a different delimiter; this check only inspects the \<name>\ form.
$bpFinalLines = [IO.File]::ReadAllLines($bpFile)
$bpFinal = $bpFinalLines -join "`n"
$bpPlaceholders = [System.Collections.Generic.HashSet[string]]::new()
foreach ($m in [regex]::Matches($bpFinal, '\\([A-Za-z_][A-Za-z0-9_]*)\\')) {
    [void]$bpPlaceholders.Add($m.Groups[1].Value)
}
# Collect names with at least one CONST line in the BP.
$constNames = [System.Collections.Generic.HashSet[string]]::new()
foreach ($cl in $bpFinalLines) {
    if ($cl -match '^#\s*CONST:\s*([A-Za-z_][A-Za-z0-9_]*)\s*=') {
        [void]$constNames.Add($Matches[1])
    }
}
$missing = New-Object 'System.Collections.Generic.List[string]'
foreach ($p in $bpPlaceholders) {
    if ($pivot.Contains($p)) { continue }
    if ($constNames.Contains($p)) { continue }
    [void]$missing.Add($p)
}
if ($missing.Count -gt 0) {
    throw "BP/symbols coherence check failed -- the following \<sym>\ placeholders appear in $bpFile but are missing from both ${csvFile} and any bucket-local '# CONST:' annotation: $($missing -join ', '). Generator must emit a coherent pair."
}
#endregion

#region detect column derivations (analysis only)
# For each bucket's column matrix (rows = tests/flows, cols = slot symbols),
# look for columns whose values are deterministically derivable from other
# columns. Detected forms:
#   - identity:   T == S (column duplicate)
#   - functional: T = f(S) — for every distinct value of S, T is constant
#   - concat:     T = L0 + S1 + L1 + S2 + ... + Lk (ordered, with fixed
#                 literal fillers across all rows)
# Output: <module>.derivations.log
function _TryConcatRule {
    param(
        [string[]] $TargetVals,
        [string[]] $PickedNames,
        [hashtable]$SourceVals
    )
    $nRows = $TargetVals.Length
    $refLits = $null
    for ($r = 0; $r -lt $nRows; $r++) {
        $T = $TargetVals[$r]
        $pos = 0
        $lits = New-Object 'System.Collections.Generic.List[string]'
        foreach ($n in $PickedNames) {
            $sv = $SourceVals[$n][$r]
            if ([string]::IsNullOrEmpty($sv)) { return $null }
            $idx = $T.IndexOf($sv, $pos)
            if ($idx -lt 0) { return $null }
            [void]$lits.Add($T.Substring($pos, $idx - $pos))
            $pos = $idx + $sv.Length
        }
        [void]$lits.Add($T.Substring($pos))
        $arr = $lits.ToArray()
        if ($null -eq $refLits) {
            $refLits = $arr
        } else {
            if ($arr.Length -ne $refLits.Length) { return $null }
            for ($i = 0; $i -lt $arr.Length; $i++) { if ($arr[$i] -cne $refLits[$i]) { return $null } }
        }
    }
    return $refLits
}

function _Detect-ConcatRule {
    param(
        [string[]] $TargetVals,
        [string[]] $SourceNames,
        [hashtable]$SourceVals
    )
    $nSrc = $SourceNames.Length
    $maxK = [Math]::Min(3, $nSrc)
    $nRows = $TargetVals.Length
    if ($nRows -lt 2 -or $nSrc -lt 1) { return $null }
    $T0 = $TargetVals[0]
    # Iterative DFS with row-0 prune: at each node, verify the partial pick
    # can still match TargetVals[0] in left-to-right order. Only when a
    # complete subset matches all rows with identical literal fillers do we
    # accept it.
    $stack = New-Object 'System.Collections.Generic.Stack[object]'
    # Frame: @{ Picks=[int[]]; Used=[int[]]; Pos0=[int] }
    $stack.Push(@{ Picks = @(); Used = (New-Object 'int[]' $nSrc); Pos0 = 0 })
    while ($stack.Count -gt 0) {
        $frame = $stack.Pop()
        $picks = $frame.Picks
        $used  = $frame.Used
        $pos0  = $frame.Pos0
        if ($picks.Length -gt 0) {
            $names = @($picks | ForEach-Object { $SourceNames[$_] })
            $lits = _TryConcatRule -TargetVals $TargetVals -PickedNames $names -SourceVals $SourceVals
            if ($null -ne $lits) { return @{ Sources = $names; Literals = $lits } }
        }
        if ($picks.Length -lt $maxK) {
            for ($i = $nSrc - 1; $i -ge 0; $i--) {
                if ($used[$i]) { continue }
                $sv0 = $SourceVals[$SourceNames[$i]][0]
                if ([string]::IsNullOrEmpty($sv0)) { continue }
                $idx = $T0.IndexOf($sv0, $pos0)
                if ($idx -lt 0) { continue }
                $newUsed = [int[]]::new($nSrc); [Array]::Copy($used, $newUsed, $nSrc); $newUsed[$i] = 1
                $stack.Push(@{ Picks = ($picks + $i); Used = $newUsed; Pos0 = ($idx + $sv0.Length) })
            }
        }
    }
    return $null
}

function Detect-Derivations {
    param([string]$BucketLabel,[string[]]$ColumnNames,[hashtable]$ColumnVals)
    $rules = New-Object 'System.Collections.Generic.List[string]'
    if ($ColumnNames.Length -lt 2) { return ,$rules }
    $nRows = $ColumnVals[$ColumnNames[0]].Length
    if ($nRows -lt 2) { return ,$rules }
    foreach ($t in $ColumnNames) {
        $tVals = $ColumnVals[$t]
        $tDistinct = @($tVals | Select-Object -Unique).Count
        if ($tDistinct -le 1) { continue }
        $found = $false
        # 1) Identity
        foreach ($s in $ColumnNames) {
            if ($s -eq $t) { continue }
            $sVals = $ColumnVals[$s]
            $eq = $true
            for ($r = 0; $r -lt $nRows; $r++) { if ($sVals[$r] -cne $tVals[$r]) { $eq = $false; break } }
            if ($eq) { [void]$rules.Add("$t = $s   (identical)"); $found = $true; break }
        }
        if ($found) { continue }
        # 2) Functional map (single source)
        foreach ($s in $ColumnNames) {
            if ($s -eq $t) { continue }
            $sVals = $ColumnVals[$s]
            $sDistinct = @($sVals | Select-Object -Unique).Count
            if ($tDistinct -gt $sDistinct) { continue }
            $map = @{}
            $isFn = $true
            for ($r = 0; $r -lt $nRows; $r++) {
                $sv = $sVals[$r]; $tv = $tVals[$r]
                if ($map.ContainsKey($sv)) {
                    if ($map[$sv] -cne $tv) { $isFn = $false; break }
                } else { $map[$sv] = $tv }
            }
            if ($isFn -and $map.Count -ge 2 -and $map.Count -lt $nRows) {
                $entries = @($map.Keys | Sort-Object | ForEach-Object { "$_->$($map[$_])" })
                [void]$rules.Add("$t = f($s)   { $($entries -join '; ') }")
                $found = $true
                break
            }
        }
        if ($found) { continue }
        # 3) Concat detection
        $sources = @($ColumnNames | Where-Object { $_ -ne $t })
        $srcVals = @{}
        foreach ($s in $sources) { $srcVals[$s] = $ColumnVals[$s] }
        $rule = _Detect-ConcatRule -TargetVals $tVals -SourceNames $sources -SourceVals $srcVals
        if ($null -ne $rule) {
            $parts = New-Object 'System.Collections.Generic.List[string]'
            $lits = $rule.Literals; $srcs = $rule.Sources
            if ($lits[0] -ne '') { [void]$parts.Add('"' + $lits[0] + '"') }
            for ($i = 0; $i -lt $srcs.Count; $i++) {
                [void]$parts.Add($srcs[$i])
                if ($i + 1 -lt $lits.Count -and $lits[$i + 1] -ne '') { [void]$parts.Add('"' + $lits[$i + 1] + '"') }
            }
            [void]$rules.Add("$t = $($parts -join ' + ')")
        }
    }
    return ,$rules
}

$derivSb = [System.Text.StringBuilder]::new()
[void]$derivSb.AppendLine("# Column derivations detected for $moduleName")
[void]$derivSb.AppendLine("# Format: TARGET = <rule>")
[void]$derivSb.AppendLine('')
$totalRules = 0
$bucketsWithRules = 0

function _BucketColumns {
    param($Info, [bool]$IsFlow)
    $names = New-Object 'System.Collections.Generic.List[string]'
    $vals  = @{}
    if ($IsFlow) {
        foreach ($f in $Info.Fields) {
            $nm = $f.SlotName
            if ($null -eq $nm) { continue }
            [void]$names.Add($nm); $vals[$nm] = @($f.SymValues)
        }
    } else {
        $absorbed = Get-AbsorbedSlots -BucketKey "B$($Info.BucketId)"
        foreach ($f in $Info.Fields) {
            if ($f.ContainsKey('Segments') -and $null -ne $f.Segments) {
                foreach ($s in $f.Segments) {
                    if ($s.Type -ne 'slot') { continue }
                    $nm = $s.SlotName
                    if ($null -eq $nm) { continue }
                    if ($absorbed.ContainsKey($nm)) { continue }
                    [void]$names.Add($nm); $vals[$nm] = @($s.SymValues)
                }
            } else {
                $nm = $f.SlotName
                if ($null -eq $nm) { continue }
                if ($absorbed.ContainsKey($nm)) { continue }
                [void]$names.Add($nm); $vals[$nm] = @($f.SymValues)
            }
        }
    }
    return @{ Names = $names.ToArray(); Vals = $vals }
}

foreach ($info in $bucketInfos) {
    try {
        $cols = _BucketColumns -Info $info -IsFlow $false
        if ($cols.Names.Length -lt 2) { continue }
        $rules = Detect-Derivations -BucketLabel "B$($info.BucketId)" -ColumnNames $cols.Names -ColumnVals $cols.Vals
        if ($rules.Count -gt 0) {
            $bucketsWithRules++; $totalRules += $rules.Count
            [void]$derivSb.AppendLine("# Bucket B$($info.BucketId)  template=$($info.Tests[0].Template)  tests=$($info.Tests.Count)")
            foreach ($r in $rules) { [void]$derivSb.AppendLine("  $r") }
            [void]$derivSb.AppendLine('')
        }
    } catch {
        Write-Host "  [derivations] Bucket B$($info.BucketId) skipped: $($_.Exception.Message) @ $($_.InvocationInfo.ScriptLineNumber)" -ForegroundColor Yellow
    }
}
foreach ($info in $flowBucketInfos) {
    try {
        $cols = _BucketColumns -Info $info -IsFlow $true
        if ($cols.Names.Length -lt 2) { continue }
        $rules = Detect-Derivations -BucketLabel "F$($info.BucketId)" -ColumnNames $cols.Names -ColumnVals $cols.Vals
        if ($rules.Count -gt 0) {
            $bucketsWithRules++; $totalRules += $rules.Count
            [void]$derivSb.AppendLine("# Bucket F$($info.BucketId)  type=Flow  flows=$($info.Flows.Count)")
            foreach ($r in $rules) { [void]$derivSb.AppendLine("  $r") }
            [void]$derivSb.AppendLine('')
        }
    } catch {
        Write-Host "  [derivations] Bucket F$($info.BucketId) skipped: $($_.Exception.Message) @ $($_.InvocationInfo.ScriptLineNumber)" -ForegroundColor Yellow
    }
}

Write-FileWithRetry -Path $derivFile -Content $derivSb.ToString()
Write-Host "  Derivations: $totalRules rule(s) across $bucketsWithRules bucket(s)  -> $derivFile"
#endregion

#region emit compressions.log (human-readable per-bucket tables)
$logSb = [System.Text.StringBuilder]::new()
[void]$logSb.AppendLine(('=' * 80))
[void]$logSb.AppendLine("BLUEPRINT COMPRESSION REPORT (data-driven v2)")
[void]$logSb.AppendLine("Module:    $moduleName")
[void]$logSb.AppendLine("Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm')")
[void]$logSb.AppendLine(('=' * 80))
[void]$logSb.AppendLine('')
[void]$logSb.AppendLine("Original tests : $($testBlocks.Count)")
[void]$logSb.AppendLine("Test buckets   : $($bucketInfos.Count)")
[void]$logSb.AppendLine("Original flows : $($flowBlocks.Count)")
[void]$logSb.AppendLine("Flow buckets   : $($flowBucketInfos.Count)")
[void]$logSb.AppendLine('')

function Render-BucketTable {
    param([System.Text.StringBuilder]$Out, [string]$Hdr, $Items, $Fields, [string]$NameProp)
    [void]$Out.AppendLine(('-' * 80))
    [void]$Out.AppendLine($Hdr)
    if ($Fields.Count -eq 0) {
        [void]$Out.AppendLine("  (no varying fields - single distinct entry)")
        [void]$Out.AppendLine("  Name: $($Items[0].$NameProp)")
        [void]$Out.AppendLine('')
        return
    }
    # Flatten composite fields into per-slot rows for the log table
    $rows = New-Object System.Collections.Generic.List[hashtable]
    foreach ($f in $Fields) {
        if ($f.ContainsKey('Segments') -and $null -ne $f.Segments) {
            foreach ($s in $f.Segments) {
                if ($s.Type -eq 'slot') {
                    [void]$rows.Add(@{ Slot = $s.SlotName; Field = "$($f.Field)<part>"; Pre = ''; Suf = ''; SymValues = $s.SymValues })
                }
            }
        } else {
            [void]$rows.Add(@{ Slot = $f.SlotName; Field = $f.Field; Pre = $f.Prefix; Suf = $f.Suffix; SymValues = $f.SymValues })
        }
    }
    $colW = 26
    $h = ('Slot [Field]').PadRight(36) + '|'
    for ($i = 0; $i -lt $Items.Count; $i++) { $h += (" T$i").PadRight($colW + 1) }
    [void]$Out.AppendLine($h)
    $row = 'Name'.PadRight(36) + '|'
    foreach ($it in $Items) {
        $n = $it.$NameProp
        if ($n.Length -gt $colW) { $n = $n.Substring(0, $colW - 1) + '~' }
        $row += (' ' + $n).PadRight($colW + 1)
    }
    [void]$Out.AppendLine($row)
    foreach ($r in $rows) {
        $lab = "$($r.Slot) [$($r.Field)]"
        if ($lab.Length -gt 36) { $lab = $lab.Substring(0, 35) + '~' }
        $row = $lab.PadRight(36) + '|'
        foreach ($v in $r.SymValues) {
            $vs = [string]$v
            if ($vs.Length -gt $colW) { $vs = $vs.Substring(0, $colW - 1) + '~' }
            $row += (' ' + $vs).PadRight($colW + 1)
        }
        [void]$Out.AppendLine($row)
        if ($r.Pre -or $r.Suf) {
            $pre = $r.Pre; if ($pre.Length -gt 60) { $pre = $pre.Substring(0, 59) + '~' }
            $suf = $r.Suf; if ($suf.Length -gt 60) { $suf = $suf.Substring(0, 59) + '~' }
            [void]$Out.AppendLine(("    prefix=`"" + $pre + "`"  suffix=`"" + $suf + "`""))
        }
    }
    [void]$Out.AppendLine('')
}

foreach ($info in $bucketInfos) {
    $h = "Bucket B$($info.BucketId)  type=$($info.Tests[0].TestType)  template=$($info.Tests[0].Template)  tests=$($info.Tests.Count)  varyingFields=$($info.Fields.Count)"
    Render-BucketTable -Out $logSb -Hdr $h -Items $info.Tests -Fields $info.Fields -NameProp 'Name'
    if ($consolidationsPerBucket.ContainsKey("B$($info.BucketId)")) {
        [void]$logSb.AppendLine("  Phase-2 consolidations:")
        foreach ($c in $consolidationsPerBucket["B$($info.BucketId)"]) {
            if ($c.Mode -eq 'full') {
                [void]$logSb.AppendLine("    \$($c.Alias)\ == \$($c.Primary)\  (full match - alias)")
            } else {
                [void]$logSb.AppendLine("    \$($c.Alias)\ == `"$($c.Prefix)`" + \$($c.Primary)\ + `"$($c.Suffix)`"  (substring)")
            }
        }
        [void]$logSb.AppendLine('')
    }
}
foreach ($info in $flowBucketInfos) {
    $h = "Bucket F$($info.BucketId)  type=Flow  flows=$($info.Flows.Count)  varyingFields=$($info.Fields.Count)"
    Render-BucketTable -Out $logSb -Hdr $h -Items $info.Flows -Fields $info.Fields -NameProp 'Name'
}

# ---- Symbol rules summary: per slot-name across all buckets ----
[void]$logSb.AppendLine(('=' * 80))
[void]$logSb.AppendLine("SYMBOL RULES SUMMARY (per slot name across buckets)")
[void]$logSb.AppendLine(('=' * 80))
$symStats = @{}   # slotName -> list of @{ Bucket; UniqueValues }
foreach ($info in $bucketInfos) {
    $absorbed = Get-AbsorbedSlots -BucketKey "B$($info.BucketId)"
    $slots = @(Get-BucketSlotEntries -Info $info)
    foreach ($s in $slots) {
        if ($absorbed.ContainsKey($s.Name)) { continue }
        $uv = @($s.Values | Sort-Object -Unique)
        if (-not $symStats.ContainsKey($s.Name)) { $symStats[$s.Name] = New-Object System.Collections.Generic.List[hashtable] }
        [void]$symStats[$s.Name].Add(@{ Bucket = "B$($info.BucketId)"; UniqueValues = $uv })
    }
}
foreach ($name in ($symStats.Keys | Sort-Object)) {
    $entries = $symStats[$name]
    $counts = @($entries | ForEach-Object { $_.UniqueValues.Count })
    $minN = ($counts | Measure-Object -Minimum).Minimum
    $maxN = ($counts | Measure-Object -Maximum).Maximum
    # Find the most common value-set signature
    $sigGroups = @{}
    foreach ($e in $entries) {
        $sig = ($e.UniqueValues -join ',')
        if (-not $sigGroups.ContainsKey($sig)) { $sigGroups[$sig] = New-Object System.Collections.Generic.List[string] }
        [void]$sigGroups[$sig].Add($e.Bucket)
    }
    $top = $sigGroups.GetEnumerator() | Sort-Object { -$_.Value.Count } | Select-Object -First 1
    $topBuckets = $top.Value
    $exceptionEntries = @($entries | Where-Object { ($_.UniqueValues -join ',') -ne $top.Key })
    [void]$logSb.AppendLine("`n$name :")
    [void]$logSb.AppendLine("  appears in $($entries.Count) bucket(s); distinct values per bucket: min=$minN max=$maxN")
    $topVals = $top.Key
    if ($topVals.Length -gt 80) { $topVals = $topVals.Substring(0, 79) + '~' }
    [void]$logSb.AppendLine("  rule: $($topBuckets.Count)/$($entries.Count) buckets have value-set [$topVals]")
    if ($exceptionEntries.Count -gt 0) {
        $shownEx = 0
        foreach ($e in $exceptionEntries) {
            $shownEx++
            if ($shownEx -gt 5) { [void]$logSb.AppendLine("    ...and $($exceptionEntries.Count - 5) more exceptions"); break }
            $ev = ($e.UniqueValues -join ',')
            if ($ev.Length -gt 80) { $ev = $ev.Substring(0, 79) + '~' }
            [void]$logSb.AppendLine("    exception in $($e.Bucket): [$ev]")
        }
    }
}
[void]$logSb.AppendLine('')

Write-FileWithRetry -Path $logFile -Content $logSb.ToString()
Write-Host "  Log written: $logFile"

# Sidecar: per-instance original bin/ctr/bnum values used to restore real
# values during Expand so the emitted .mtpl is build-valid even though the
# BP itself uses normalized __BIN__/__CTR__/__BNUM__ placeholders.
$binmapFile = Join-Path $OutputDir "$moduleName.binmap.json"
$binmap = @{
    tests    = $binmapTests
    flows    = $binmapFlows
    defaults = @{
        SetPointsPreInstance  = $globalDefaultPre
        SetPointsPostInstance = $globalDefaultPost
    }
}
$binmap | ConvertTo-Json -Depth 4 -Compress | Set-Content -Path $binmapFile -Encoding UTF8
Write-Host "  Binmap written: $binmapFile (tests=$($binmapTests.Count), flows=$($binmapFlows.Count))"
#endregion

#region emit prompt
$pr = [System.Text.StringBuilder]::new()
[void]$pr.AppendLine(('=' * 80))
[void]$pr.AppendLine("MTPL BLUEPRINT (v2 data-driven)")
[void]$pr.AppendLine("Module: $moduleName")
[void]$pr.AppendLine("Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm')")
[void]$pr.AppendLine(('=' * 80))
[void]$pr.AppendLine('')
[void]$pr.AppendLine("The _bp.mtpl contains one representative block per bucket. Each block is")
[void]$pr.AppendLine("preceded by:    # BP_BUCKET: B<id> tests=<count>")
[void]$pr.AppendLine("Symbol values per test live in $moduleName.symbols.csv.")
[void]$pr.AppendLine("Use Expand-BluePrint.ps1 to reconstruct the full .mtpl.")
[void]$pr.AppendLine('')
[void]$pr.AppendLine('Notes:')
foreach ($n in $notes) { [void]$pr.AppendLine("  - $n") }
[IO.File]::WriteAllText($promptFile, $pr.ToString())
#endregion

Write-Host ""
Write-Host "=== Done ==="
