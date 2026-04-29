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
      <module>.mtpl.bp          - compressed test programme
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
    [string]$OutputDir
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

#region paths
$InputMtpl  = (Resolve-Path $InputMtpl).Path
$ConfigFile = (Resolve-Path $ConfigFile).Path
$moduleName = [IO.Path]::GetFileNameWithoutExtension($InputMtpl)
if (-not $OutputDir) { $OutputDir = Join-Path (Split-Path $InputMtpl) 'BluePrint' }
if (-not (Test-Path $OutputDir)) { New-Item -ItemType Directory $OutputDir -Force | Out-Null }

$bpFile     = Join-Path $OutputDir "$moduleName.mtpl.bp"
$csvFile    = Join-Path $OutputDir "$moduleName.symbols.csv"
$logFile    = Join-Path $OutputDir "$moduleName.compressions.log"
$promptFile = Join-Path $OutputDir "$moduleName.prompt.txt"

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
    # Replace per-instance bin / counter / baseNumber values with a single
    # canonical token so blocks that differ only in those values can merge.
    # Returns the normalized line.
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
    return $l
}

function Normalize-BodyLines {
    param([System.Collections.Generic.List[string]]$Body)
    $out = [System.Collections.Generic.List[string]]::new()
    foreach ($l in $Body) { [void]$out.Add((Normalize-BinCounterLine -Line $l)) }
    return $out
}

function Extract-BinCtrValues {
    # Return ordered list of original bin/ctr/bnum *values* (in body order),
    # i.e. exactly the values that Normalize-BinCounterLine replaced with
    # __BIN__/__CTR__/__BNUM__ placeholders.
    param([System.Collections.Generic.List[string]]$Body)
    $out = [System.Collections.Generic.List[string]]::new()
    foreach ($l in $Body) {
        if ($l -match '^\s*(?:##EDC##\s*)?SetBin\s+(.+?)\s*;\s*$') {
            [void]$out.Add($Matches[1])
        } elseif ($l -match '^\s*(?:##EDC##\s*)?IncrementCounters\s+(.+?)\s*;\s*$') {
            [void]$out.Add($Matches[1])
        } elseif ($l -match '^\s*BaseNumbers\s*=\s*"([^"]*)"\s*;\s*$') {
            [void]$out.Add($Matches[1])
        }
    }
    return $out
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
    # (param-name list AND non-param body lines verbatim).
    param($Block)
    $params = Parse-Params -Lines $Block.BodyLines
    $paramKey = ($params | ForEach-Object { $_.Name }) -join '|'
    $cmtKey = ($Block.CommentLines | ForEach-Object { ($_ -replace '\s+', ' ').Trim() }) -join '||'
    # Non-param body lines (comments inside body, blank lines, brace lines, etc.)
    # — must match exactly across bucket members.
    $nonParam = [System.Collections.Generic.List[string]]::new()
    for ($i = 0; $i -lt $Block.BodyLines.Count; $i++) {
        $l = $Block.BodyLines[$i]
        if ($l -match '^(\s*\w+\s*=\s*)"[^"]*"\s*;?\s*$') {
            $nonParam.Add("<PQ:$($Matches[1])>")
        } elseif ($l -match '^(\s*\w+\s*=\s*).+?\s*;\s*$') {
            $nonParam.Add("<PU:$($Matches[1])>")
        } elseif ($l -match '^\s*(CSharpTest|MultiTrialTest)\s+') {
            # Header line - shape only (template name kept; instance name drop)
            $nonParam.Add('<H>')
        } else {
            $nonParam.Add(($l -replace '\s+', ' ').Trim())
        }
    }
    $structKey = $nonParam -join '||'
    # Instance-name token-shape: sequence of separators ('_' / ',') in the
    # instance name. Tests with the same body shape but different name shapes
    # go to separate sub-buckets so Decompose-OnSeparators can produce one
    # column per varying token.
    $nameShape = ''
    foreach ($ch in $Block.Name.ToCharArray()) {
        if ($ch -eq '_' -or $ch -eq ',') { $nameShape += $ch }
    }
    return "$($Block.TestType)|$($Block.Template)|$paramKey|$cmtKey|$structKey|$nameShape"
}

function CsvEscape {
    param([string]$s)
    if ($null -eq $s) { return '' }
    if ($s -match '[",\r\n]') { return '"' + ($s -replace '"','""') + '"' }
    return $s
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
        $info.Fields.Add(@{
            Field     = '__FLOWNAME__'
            LineIdx   = -1
            TokenIdx  = -1
            Prefix    = $p
            Suffix    = $s
            SymValues = @($sv)
        })
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
            $info.Fields.Add(@{
                Field     = "L${li}T${tk}"
                LineIdx   = $li
                TokenIdx  = $tk
                Prefix    = $pre
                Suffix    = $suf
                SymValues = @($sv)
            })
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

$totalFlowFields = 0
foreach ($_fbi in $flowBucketInfos) { $totalFlowFields += $_fbi.Fields.Count }
Write-Host "  Total varying flow fields across buckets: $totalFlowFields"
#endregion

#region emit BP file
$sb = [System.Text.StringBuilder]::new()
[void]$sb.AppendLine(($preambleLines -join "`n"))
[void]$sb.AppendLine('')

foreach ($info in $bucketInfos) {
    $rep = $info.Tests[0]
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

    foreach ($c in $rep.CommentLines) { [void]$sb.AppendLine($c) }
    foreach ($l in $body)             { [void]$sb.AppendLine($l) }
}

# Flow buckets � use same compress mechanism (one representative per bucket).
[void]$sb.AppendLine('')
[void]$sb.AppendLine('')
foreach ($info in $flowBucketInfos) {
    $rep = $info.Flows[0]
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

    foreach ($c in $rep.CommentLines) { [void]$sb.AppendLine($c) }
    foreach ($l in $body)             { [void]$sb.AppendLine($l) }
}

[IO.File]::WriteAllText($bpFile, $sb.ToString().TrimEnd() + "`r`n")
$bpLineCount = [IO.File]::ReadAllLines($bpFile).Count
Write-Host "  BP written: $bpFile ($bpLineCount lines, was $($rawLines.Count))"
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

[IO.File]::WriteAllLines($csvFile, $csvLines.ToArray())
Write-Host "  CSV written: $csvFile ($($bucketInfos.Count) test buckets, $($flowBucketInfos.Count) flow buckets)"
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
}
foreach ($info in $flowBucketInfos) {
    $h = "Bucket F$($info.BucketId)  type=Flow  flows=$($info.Flows.Count)  varyingFields=$($info.Fields.Count)"
    Render-BucketTable -Out $logSb -Hdr $h -Items $info.Flows -Fields $info.Fields -NameProp 'Name'
}

[IO.File]::WriteAllText($logFile, $logSb.ToString())
Write-Host "  Log written: $logFile"

# Sidecar: per-instance original bin/ctr/bnum values used to restore real
# values during Expand so the emitted .mtpl is build-valid even though the
# BP itself uses normalized __BIN__/__CTR__/__BNUM__ placeholders.
$binmapFile = Join-Path $OutputDir "$moduleName.binmap.json"
$binmap = @{ tests = $binmapTests; flows = $binmapFlows }
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
[void]$pr.AppendLine("The .mtpl.bp contains one representative block per bucket. Each block is")
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
