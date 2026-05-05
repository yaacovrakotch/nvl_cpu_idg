<#
.SYNOPSIS
    Cross-flow aligned BluePrint generator (v2). Treats N user-supplied flows
    as parallel structures and produces ONE templated BP plus ONE symbol table
    where rows = symbols, columns = the input flows, cells = per-flow values.

.DESCRIPTION
    Pipeline (incorporates learnings 1-4, 7-26 from Generate-BluePrint.ps1):

      1. Slice each input flow's body lines (and bodies of referenced tests
         unless -FlowsOnly) into a per-flow stream.

      2. PRE-ALIGNMENT NORMALIZATION (per line, in this order):
            (1) SetBin              -> __BIN__       (sidecar: per-flow values)
            (2) IncrementCounters   -> __CTR__       (sidecar)
            (3) BaseNumbers="..."   -> "__BNUM__"    (sidecar)
            (4) BypassPort=...      -> __BYPASS__    (sidecar)
            (7) Compact-Whitespace  -- collapse internal whitespace runs to a
                                       single space, preserve indent hint
         All four placeholder lines are byte-identical across flows -> they
         do NOT generate any symbols.  Original per-flow values are written
         to <slice>.binmap.json so an Expand step can restore them.

      3. Progressive pairwise LCS over normalized lines (digits collapsed to
         '#', whitespace single-spaced) builds the N-way alignment.

      4. Per aligned column:
            - all identical, no gaps  -> emit literal line
            - some gaps               -> presence-symbol (kind=opt)
            - non-null but differ     -> tokenize & per token-position emit
                                         literals OR varying symbols, with
                                         char-level prefix/suffix peel,
                                         snap-back to word boundary (15)
                                         and MIN/MAX rescue (16).

      5. Symbol allocator (deduped by core-values tuple) tracks BOTH the
         peeled "core" (for BP placement) AND the FULL per-flow token value
         (for the CSV) so the symbols.csv is human-readable.
            - (17) Vocab naming: if the unique value set is a subset of any
                   bp-config.json symbol, use that symbol name instead of S<n>.

      6. (23) Derivation pass: detect symbols whose per-flow values are a
         constant string transform of another symbol; emit derivations log.

      7. (25/26) Sidecar JSON binmap with per-flow original bin/ctr/bnum/
         bypass values for downstream Expand.

    Outputs (in <module>\BluePrint\block\):
      <slice>_bp.mtpl            templated single representation
      <slice>_symbols.csv        rows=symbols, cols=Symbol,Kind,Pre,Suf,<flows>
      <slice>.binmap.json        per-flow original values
      <slice>.derivations.log    candidate symbol-derivation report
      <slice>.log                alignment stats + diagnostics

.PARAMETER InputMtpl
    Source .mtpl file (or .mtpl_orig) holding all the flows.

.PARAMETER Flows
    One or more flow names to align together.

.PARAMETER Tag
    Short label appended to output filenames. Default 'sel'.

.PARAMETER OutputDir
    Where to write outputs. Default <module>\BluePrint\block\.

.PARAMETER ConfigFile
    Optional bp-config.json (used only for vocabulary symbol-name hints).

.PARAMETER FlowsOnly
    When set, skip the bodies of tests referenced by FlowItems and align
    only the flow definitions themselves.

.EXAMPLE
    .\Generate-BluePrintBlockAligned.ps1 `
        -InputMtpl ..\ARR\ARR_ATOM_CXX\ARR_ATOM_CXX.mtpl `
        -Flows ARR_ATOM_CXX_F1XAT,ARR_ATOM_CXX_F2XAT,ARR_ATOM_CXX_F3XAT `
        -Tag F1F2F3XAT `
        -ConfigFile ..\ARR\ARR_ATOM_CXX\BluePrint\bp-config.json
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory)] [string]   $InputMtpl,
    [Parameter(Mandatory)] [string[]] $Flows,
    [string] $Tag = 'sel',
    [string] $OutputDir,
    [string] $ConfigFile,
    [switch] $FlowsOnly
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

#region paths -------------------------------------------------------------------
$InputMtpl  = (Resolve-Path $InputMtpl).Path
$moduleName = [IO.Path]::GetFileNameWithoutExtension($InputMtpl)
$moduleDir  = Split-Path $InputMtpl
if (-not $OutputDir) { $OutputDir = Join-Path $moduleDir 'BluePrint\block' }
if (-not (Test-Path $OutputDir)) { New-Item -ItemType Directory $OutputDir -Force | Out-Null }

$sliceName = "${moduleName}_block_${Tag}_aligned"
$bpFile    = Join-Path $OutputDir "$sliceName`_bp.mtpl"
$csvFile   = Join-Path $OutputDir "$sliceName`_symbols.csv"
$binFile   = Join-Path $OutputDir "$sliceName.binmap.json"
$derivFile = Join-Path $OutputDir "$sliceName.derivations.log"
$logFile   = Join-Path $OutputDir "$sliceName.log"

Write-Host "=== Cross-flow Aligned BluePrint Generator (v2) ==="
Write-Host "Module : $moduleName"
Write-Host "Source : $InputMtpl"
Write-Host "Flows  : $($Flows -join ', ')"
Write-Host "Output : $OutputDir"
#endregion

#region load vocab from optional config ----------------------------------------
$vocab = [ordered]@{}
if ($ConfigFile -and (Test-Path $ConfigFile)) {
    $cfg = Get-Content -Raw $ConfigFile | ConvertFrom-Json
    if ($cfg.PSObject.Properties['symbols']) {
        foreach ($s in $cfg.symbols) {
            $vocab[$s.name] = @($s.values | ForEach-Object { ($_ -replace '\s*\(.*\)', '').Trim() })
        }
    }
    Write-Host "  Vocabulary symbols loaded: $($vocab.Count)"
}
#endregion

#region parse mtpl --------------------------------------------------------------
$rawLines = [IO.File]::ReadAllLines($InputMtpl)

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

function Parse-BlockEnd {
    param([string[]]$Lines, [int]$StartIdx)
    $depth = 0; $opened = $false
    $j = $StartIdx
    while ($j -lt $Lines.Count) {
        $depth += ([regex]::Matches($Lines[$j], '\{')).Count
        $depth -= ([regex]::Matches($Lines[$j], '\}')).Count
        if ($depth -gt 0) { $opened = $true }
        if ($opened -and $depth -le 0) { return $j }
        $j++
    }
    return $j - 1
}

$countersEnd = Find-EndOfCounters -Lines $rawLines
$testIndex = @{}
$flowIndex = @{}

$i = $countersEnd + 1
$inFlowSection = $false
while ($i -lt $rawLines.Count) {
    $ln = $rawLines[$i]
    if (-not $inFlowSection -and ($ln -match '^\s*CSharpTest\s+\S+\s+(\S+)' -or $ln -match '^\s*MultiTrialTest\s+(\S+)\s*$')) {
        $name = $Matches[1].Trim()
        $end  = Parse-BlockEnd -Lines $rawLines -StartIdx $i
        $testIndex[$name] = @{ Start = $i; End = $end }
        $i = $end + 1; continue
    }
    if ($ln -match '^\s*Flow\s+(\S+)') {
        $inFlowSection = $true
        $name = $Matches[1]
        $end  = Parse-BlockEnd -Lines $rawLines -StartIdx $i
        $flowIndex[$name] = @{ Start = $i; End = $end }
        $i = $end + 1; continue
    }
    $i++
}

Write-Host "  Indexed $($testIndex.Count) test(s), $($flowIndex.Count) flow(s) in source."

$missing = @($Flows | Where-Object { -not $flowIndex.ContainsKey($_) })
if ($missing.Count -gt 0) { throw "Flow(s) not found: $($missing -join ', ')" }
#endregion

#region pre-alignment line normalizers (learnings 1-4 + 7) ---------------------

function Compact-Whitespace {
    # Learning 7: collapse internal runs of spaces/tabs to a single space,
    # strip trailing whitespace, preserve at most ONE leading space when the
    # original had any indentation.
    param([string]$Line)
    if ($null -eq $Line -or $Line.Length -eq 0) { return $Line }
    $hadIndent = ($Line -match '^[ \t]')
    $s = ($Line -replace '[ \t]+', ' ').TrimEnd()
    if (-not $hadIndent -and $s.StartsWith(' ')) { $s = $s.Substring(1) }
    if ($hadIndent -and -not $s.StartsWith(' ')) { $s = ' ' + $s }
    return $s
}

function Normalize-BinCounterLine {
    # Learnings 1-4: replace per-instance bin/counter/baseNumber/BypassPort
    # values with canonical placeholders so they don't appear as differences.
    # Returns @{ Line = <normalized>; Kind = <bin|ctr|bnum|bypass|''>; Value = <original or $null> }
    # NOTE: BypassPort regex allows EMPTY value (BypassPort = ;) so empty-value
    # cases also normalize uniformly; empty/whitespace becomes the global default.
    param([string]$Line, [string]$DefaultBypass = '1')
    $l = $Line
    if ($l -match '^(\s*(?:##EDC##\s*)?SetBin\s+)(.+?)(\s*;\s*)$') {
        return @{ Line = ($Matches[1] + '__BIN__' + $Matches[3]); Kind = 'bin'; Value = $Matches[2] }
    }
    if ($l -match '^(\s*(?:##EDC##\s*)?IncrementCounters\s+)(.+?)(\s*;\s*)$') {
        return @{ Line = ($Matches[1] + '__CTR__' + $Matches[3]); Kind = 'ctr'; Value = $Matches[2] }
    }
    if ($l -match '^(\s*BaseNumbers\s*=\s*)"([^"]*)"(\s*;\s*)$') {
        return @{ Line = ($Matches[1] + '"__BNUM__"' + $Matches[3]); Kind = 'bnum'; Value = $Matches[2] }
    }
    if ($l -match '^(\s*BypassPort\s*=\s*)(.*?)(\s*;\s*)$') {
        $val = $Matches[2]
        if ([string]::IsNullOrWhiteSpace($val)) { $val = $DefaultBypass }
        return @{ Line = ($Matches[1] + '__BYPASS__' + $Matches[3]); Kind = 'bypass'; Value = $val }
    }
    return @{ Line = $l; Kind = ''; Value = $null }
}
#endregion

#region pick global default BypassPort from source -----------------------------
# First non-empty BypassPort value seen anywhere in the source mtpl. Used both
# (a) as the substitute when a BypassPort line has an empty value, and
# (b) as the value for synthetic BypassPort lines injected into test bodies
#     that don't declare BypassPort at all.
$globalDefaultBypass = '1'
foreach ($_l in $rawLines) {
    if ($_l -match '^\s*BypassPort\s*=\s*(\S.*?)\s*;\s*$') {
        $globalDefaultBypass = $Matches[1]; break
    }
}
Write-Host "  Default BypassPort value: $globalDefaultBypass"
#endregion

#region build per-flow streams (with normalization + binmap collection) --------

# binmap[$flowName] = ordered list of @{ Kind; Value } in body-order
$binmap = [ordered]@{}

function Build-Stream {
    param([string]$FlowName)
    $info = $flowIndex[$FlowName]
    $flowBodyLines = New-Object 'System.Collections.Generic.List[string]'
    $testBodyLines = New-Object 'System.Collections.Generic.List[string]'
    $flowBin       = New-Object 'System.Collections.Generic.List[hashtable]'
    $injectedCount = 0

    # 1) Collect referenced test bodies in SOURCE-MTPL ORDER (so all tests
    #    appear before all flows in the BP, matching .mtpl convention).
    if (-not $FlowsOnly) {
        $refs = New-Object 'System.Collections.Generic.HashSet[string]'
        for ($k = $info.Start; $k -le $info.End; $k++) {
            $l = $rawLines[$k]
            if ($l -match '^\s*(?:DUTFlowItem|FlowItem)\s+\S+\s+(\S+)') {
                $ref = $Matches[1]
                if ($testIndex.ContainsKey($ref)) { [void]$refs.Add($ref) }
            }
        }
        $orderedRefs = $refs | Sort-Object { $testIndex[$_].Start }
        foreach ($ref in $orderedRefs) {
            [void]$testBodyLines.Add("## TEST_BODY $ref")
            $tinfo = $testIndex[$ref]
            # Buffer body lines so we can decide on BypassPort injection
            # before the closing brace.
            $body  = New-Object 'System.Collections.Generic.List[hashtable]'   # @{ Line; Kind; Value }
            $sawBypass = $false
            $closeIdx  = -1
            for ($t = $tinfo.Start; $t -le $tinfo.End; $t++) {
                $raw = $rawLines[$t]
                $n   = Normalize-BinCounterLine -Line $raw -DefaultBypass $globalDefaultBypass
                [void]$body.Add(@{ Line = (Compact-Whitespace -Line $n.Line); Kind = $n.Kind; Value = $n.Value })
                if ($n.Kind -eq 'bypass') { $sawBypass = $true }
            }
            # Locate the closing brace line of THIS test body (last line that's
            # only `}` after compact-whitespace; otherwise last line).
            for ($q = $body.Count - 1; $q -ge 0; $q--) {
                $bln = $body[$q].Line
                if ($null -ne $bln -and $bln.Trim() -eq '}') { $closeIdx = $q; break }
            }
            if (-not $sawBypass) {
                $injectLine = '   BypassPort = __BYPASS__;'
                $injectRec  = @{ Line = $injectLine; Kind = 'bypass'; Value = $globalDefaultBypass }
                if ($closeIdx -ge 0) { $body.Insert($closeIdx, $injectRec) }
                else                 { [void]$body.Add($injectRec) }
                $injectedCount++
            }
            foreach ($rec in $body) {
                [void]$testBodyLines.Add($rec.Line)
                if ($rec.Kind) { [void]$flowBin.Add(@{ Kind = $rec.Kind; Value = $rec.Value }) }
            }
        }
    }

    # 2) Then the flow body itself.
    for ($k = $info.Start; $k -le $info.End; $k++) {
        $raw = $rawLines[$k]
        $n   = Normalize-BinCounterLine -Line $raw -DefaultBypass $globalDefaultBypass
        if ($n.Kind) { [void]$flowBin.Add(@{ Kind = $n.Kind; Value = $n.Value }) }
        [void]$flowBodyLines.Add((Compact-Whitespace -Line $n.Line))
    }

    $binmap[$FlowName] = $flowBin
    if ($injectedCount -gt 0) {
        Write-Host ("    [{0}] injected {1} synthetic BypassPort line(s)" -f $FlowName, $injectedCount)
    }
    $combined = New-Object 'System.Collections.Generic.List[string]'
    foreach ($l in $testBodyLines) { [void]$combined.Add($l) }
    foreach ($l in $flowBodyLines) { [void]$combined.Add($l) }
    return $combined.ToArray()
}

$streams = @()
foreach ($f in $Flows) { $streams += ,(Build-Stream -FlowName $f) }
for ($s = 0; $s -lt $streams.Count; $s++) {
    Write-Host ("  Stream {0,-30} -> {1,5} lines, binmap entries: {2}" -f $Flows[$s], $streams[$s].Count, $binmap[$Flows[$s]].Count)
}
#endregion

#region progressive N-way LCS alignment ----------------------------------------
function Normalize-LcsKey {
    param([string]$L)
    if ($null -eq $L) { return $null }
    $s = $L -replace '\d+', '#'
    return ($s -replace '\s+', ' ').Trim()
}

function Lcs-Pairs {
    param([string[]]$A, [string[]]$B)
    $n = $A.Count; $m = $B.Count
    $dp = New-Object 'int[,]' ($n + 1), ($m + 1)
    for ($p = 0; $p -lt $n; $p++) {
        for ($q = 0; $q -lt $m; $q++) {
            if ($A[$p] -ceq $B[$q]) {
                $dp[($p+1),($q+1)] = $dp[$p,$q] + 1
            } else {
                $a1 = $dp[$p,($q+1)]; $a2 = $dp[($p+1),$q]
                $dp[($p+1),($q+1)] = [Math]::Max($a1, $a2)
            }
        }
    }
    $out = New-Object 'System.Collections.Generic.List[hashtable]'
    $p = $n; $q = $m
    while ($p -gt 0 -or $q -gt 0) {
        if ($p -gt 0 -and $q -gt 0 -and $A[$p-1] -ceq $B[$q-1]) {
            $out.Insert(0, @{ A = $p-1; B = $q-1 }); $p--; $q--
        } elseif ($q -gt 0 -and ($p -eq 0 -or $dp[$p,($q-1)] -ge $dp[($p-1),$q])) {
            $out.Insert(0, @{ A = $null; B = $q-1 }); $q--
        } else {
            $out.Insert(0, @{ A = $p-1; B = $null }); $p--
        }
    }
    return $out
}

$alignment = New-Object 'System.Collections.Generic.List[object]'
foreach ($l in $streams[0]) { [void]$alignment.Add(@($l)) }

for ($si = 1; $si -lt $streams.Count; $si++) {
    $A = @($alignment | ForEach-Object {
        $key = $null
        foreach ($x in $_) { if ($null -ne $x) { $key = Normalize-LcsKey $x; break } }
        if ($null -eq $key) { '' } else { $key }
    })
    $B = @($streams[$si] | ForEach-Object { Normalize-LcsKey $_ })
    $pairs = Lcs-Pairs -A $A -B $B
    $newAlign = New-Object 'System.Collections.Generic.List[object]'
    foreach ($pair in $pairs) {
        $aIdx = $pair.A; $bIdx = $pair.B
        if ($null -ne $aIdx -and $null -ne $bIdx) {
            [void]$newAlign.Add(@($alignment[$aIdx]) + @($streams[$si][$bIdx]))
        } elseif ($null -ne $aIdx) {
            [void]$newAlign.Add(@($alignment[$aIdx]) + @($null))
        } else {
            $extra = New-Object 'System.Collections.Generic.List[object]'
            for ($z = 0; $z -lt $si; $z++) { [void]$extra.Add($null) }
            [void]$extra.Add($streams[$si][$bIdx])
            [void]$newAlign.Add($extra.ToArray())
        }
    }
    $alignment = $newAlign
}

$N = $streams.Count
Write-Host "  Aligned columns: $($alignment.Count) (across $N flow stream(s))"
#endregion

#region symbol allocator (learnings 14, 15, 16, 17) ----------------------------
$script:nextId = 1
$script:usedNames = @{}
$script:symbolByKey = @{}
$script:symbols = New-Object 'System.Collections.Generic.List[hashtable]'

function Common-Prefix {
    param([string[]]$Strs)
    if (-not $Strs -or $Strs.Count -eq 0) { return '' }
    $p = $Strs[0]
    for ($i = 1; $i -lt $Strs.Count; $i++) {
        $s = $Strs[$i]; if ($null -eq $s) { return '' }
        $maxLen = [Math]::Min($p.Length, $s.Length); $j = 0
        while ($j -lt $maxLen -and $p[$j] -ceq $s[$j]) { $j++ }
        $p = $p.Substring(0, $j)
        if ($p.Length -eq 0) { return '' }
    }
    return $p
}

function Common-Suffix {
    param([string[]]$Strs)
    if (-not $Strs -or $Strs.Count -eq 0) { return '' }
    $rev = foreach ($s in $Strs) { if ($null -eq $s) { '' } else { $arr = $s.ToCharArray(); [Array]::Reverse($arr); -join $arr } }
    $rp  = Common-Prefix -Strs @($rev)
    $arr = $rp.ToCharArray(); [Array]::Reverse($arr)
    return -join $arr
}

function Find-VocabName {
    # Learning 17. Returns vocab key whose value-set is a SUPERSET of $UniqueValues.
    param([string[]]$UniqueValues)
    if ($vocab.Count -eq 0) { return $null }
    foreach ($entry in $vocab.GetEnumerator()) {
        $vSet = [System.Collections.Generic.HashSet[string]]::new([string[]]@($entry.Value), [System.StringComparer]::OrdinalIgnoreCase)
        $isSubset = $true
        foreach ($v in $UniqueValues) { if (-not $vSet.Contains($v)) { $isSubset = $false; break } }
        if ($isSubset) { return $entry.Key }
    }
    return $null
}

function New-SymbolName {
    # Pick a placeholder name. Preference:
    #   1. Vocab match (e.g. FREQ_CORNER from bp-config.json)
    #   2. Joined per-flow CORE values, separated by '|', e.g. F1|F2|F3 ;
    #      capped to 40 chars to stay readable. This makes the BP self-
    #      documenting -- you can see all per-flow values right where the
    #      placeholder sits, instead of a meaningless S<n>.
    #   3. Fallback to S<n> if the joined form would be unsafe / too long.
    param([string[]]$UniqueValues, [string[]]$CoreValuesPerFlow = $null)
    $vName = Find-VocabName -UniqueValues $UniqueValues
    if ($vName -and -not $script:usedNames.ContainsKey($vName)) {
        $script:usedNames[$vName] = $true
        return $vName
    }
    if ($CoreValuesPerFlow) {
        $joined = ($CoreValuesPerFlow | ForEach-Object {
            $v = "$_"
            if ($v.Length -gt 12) { $v.Substring(0, 12) + '..' } else { $v }
        }) -join '|'
        if ($joined.Length -gt 0 -and $joined.Length -le 60 -and $joined -notmatch '[\\\r\n]') {
            $cand = $joined
            if (-not $script:usedNames.ContainsKey($cand)) {
                $script:usedNames[$cand] = $true
                return $cand
            }
            $n = 2
            while ($script:usedNames.ContainsKey("$cand#$n")) { $n++ }
            $script:usedNames["$cand#$n"] = $true
            return "$cand#$n"
        }
    }
    $name = "S$($script:nextId)"; $script:nextId++
    while ($script:usedNames.ContainsKey($name)) { $name = "S$($script:nextId)"; $script:nextId++ }
    $script:usedNames[$name] = $true
    return $name
}

function Apply-MinMaxRescue {
    # Learning 16.
    param([hashtable]$Alloc)
    $vals = @($Alloc.Core)
    if ($vals.Count -lt 2) { return }
    $uniq = @($vals | Sort-Object -Unique)
    if ($uniq.Count -ne 2) { return }
    if (-not (($uniq -contains 'IN') -and ($uniq -contains 'AX'))) { return }
    if (-not $Alloc.Pre) { return }
    if ($Alloc.Pre.Length -lt 1 -or $Alloc.Pre[$Alloc.Pre.Length - 1] -ne 'M') { return }
    $Alloc.Pre  = $Alloc.Pre.Substring(0, $Alloc.Pre.Length - 1)
    $Alloc.Core = @($vals | ForEach-Object { 'M' + $_ })
}

function Snap-PrefixSuffix {
    # Learning 15. Snap to separator (_,) or word/non-word boundary.
    param([string]$Pre, [string]$Suf, [string[]]$Values)
    $isWord = { param($c) $c -match '[A-Za-z0-9]' }
    while ($Pre.Length -gt 0) {
        $last = $Pre[$Pre.Length - 1]
        $nextChars = $Values | ForEach-Object { if ($_.Length -gt $Pre.Length) { $_[$Pre.Length] } else { '' } }
        $boundaryOk = $false
        if ($last -eq '_' -or $last -eq ',') { $boundaryOk = $true }
        else {
            $lastIsW = (& $isWord $last); $allBoundary = $true
            foreach ($nc in $nextChars) {
                if ($nc -eq '') { continue }
                $ncIsW = (& $isWord $nc)
                if ($lastIsW -eq $ncIsW) { $allBoundary = $false; break }
            }
            if ($allBoundary) { $boundaryOk = $true }
        }
        if ($boundaryOk) { break }
        $Pre = $Pre.Substring(0, $Pre.Length - 1)
    }
    while ($Suf.Length -gt 0) {
        $first = $Suf[0]
        $prevChars = $Values | ForEach-Object {
            $pos = $_.Length - $Suf.Length
            if ($pos -gt 0) { $_[$pos - 1] } else { '' }
        }
        $boundaryOk = $false
        if ($first -eq '_' -or $first -eq ',') { $boundaryOk = $true }
        else {
            $firstIsW = (& $isWord $first); $allBoundary = $true
            foreach ($pc in $prevChars) {
                if ($pc -eq '') { continue }
                $pcIsW = (& $isWord $pc)
                if ($firstIsW -eq $pcIsW) { $allBoundary = $false; break }
            }
            if ($allBoundary) { $boundaryOk = $true }
        }
        if ($boundaryOk) { break }
        $Suf = $Suf.Substring(1)
    }
    return @{ Pre = $Pre; Suf = $Suf }
}

function Allocate-Symbol {
    # Returns @{ Name; Pre; Suf; Core; Full } where:
    #   Pre/Suf : literal text consumed into the surrounding BP context
    #   Core    : per-flow VARYING substring (used for dedup, NOT shown in CSV)
    #   Full    : the FULL per-flow value (shown in CSV) -- user-friendly
    # Symbols are deduped on (Kind, Core-tuple) so one S<n> represents one
    # recurring distinction across the whole flow set.
    param([string[]]$Values, [string]$Kind = 'tok')

    $full = @($Values)
    $pre  = Common-Prefix -Strs $Values
    $suf  = Common-Suffix -Strs $Values
    $minL = ($Values | ForEach-Object { $_.Length } | Measure-Object -Minimum).Minimum
    while ($pre.Length + $suf.Length -gt $minL) {
        if ($suf.Length -ge $pre.Length) { $suf = $suf.Substring(1) } else { $pre = $pre.Substring(0, $pre.Length - 1) }
    }
    $snapped = Snap-PrefixSuffix -Pre $pre -Suf $suf -Values $Values
    $pre = $snapped.Pre; $suf = $snapped.Suf
    $core = @($Values | ForEach-Object { $_.Substring($pre.Length, $_.Length - $pre.Length - $suf.Length) })

    $key = "$Kind|" + ($core -join "`u{1F}")
    if ($script:symbolByKey.ContainsKey($key)) {
        $existing = $script:symbolByKey[$key]
        return @{ Name = $existing.Name; Pre = $pre; Suf = $suf; Core = $core; Full = $full }
    }
    $alloc = @{ Name = $null; Pre = $pre; Suf = $suf; Core = $core; Full = $full; Kind = $Kind }
    Apply-MinMaxRescue -Alloc $alloc
    $alloc.Name = New-SymbolName -UniqueValues @($alloc.Core | Sort-Object -Unique) -CoreValuesPerFlow $alloc.Core

    $rec = @{ Name = $alloc.Name; Kind = $Kind; Core = $alloc.Core; Full = $full; Pre = $alloc.Pre; Suf = $alloc.Suf }
    $script:symbolByKey[$key] = $rec
    [void]$script:symbols.Add($rec)
    return $alloc
}
#endregion

#region tokenizer + per-line templating (13, 14) -------------------------------
function Tokenize-Line {
    # Word = run of [A-Za-z0-9]; everything else is a separator (so '_' splits).
    param([string]$L)
    $out = New-Object 'System.Collections.Generic.List[hashtable]'
    if ($null -eq $L) { return $out }
    $i = 0
    while ($i -lt $L.Length) {
        if ($L[$i] -match '[A-Za-z0-9]') {
            $j = $i
            while ($j -lt $L.Length -and $L[$j] -match '[A-Za-z0-9]') { $j++ }
            [void]$out.Add(@{ Type = 'word'; Text = $L.Substring($i, $j - $i) })
            $i = $j
        } else {
            $j = $i
            while ($j -lt $L.Length -and $L[$j] -notmatch '[A-Za-z0-9]') { $j++ }
            [void]$out.Add(@{ Type = 'sep'; Text = $L.Substring($i, $j - $i) })
            $i = $j
        }
    }
    return $out
}

function Render-DiffLine {
    param([string[]]$Lines)
    $tokSets = New-Object 'System.Collections.Generic.List[object]'
    foreach ($l in $Lines) { [void]$tokSets.Add(@(Tokenize-Line -L $l)) }
    $counts  = New-Object 'System.Collections.Generic.List[int]'
    foreach ($ts in $tokSets) { [void]$counts.Add($ts.Count) }
    $uniqCnt = @($counts | Sort-Object -Unique)
    if ($uniqCnt.Count -ne 1) {
        # Token-count mismatch across flows. Don't synthesize a Frankenstein
        # template that mixes tokens from different flows; just keep the first
        # flow's literal line so the BP stays buildable. The other flows'
        # version is preserved in their per-flow stream files (or by re-running
        # with a different flow listed first).
        return [string]$Lines[0]
    }
    $sb = [System.Text.StringBuilder]::new()
    $nTok = $counts[0]
    for ($p = 0; $p -lt $nTok; $p++) {
        $vals = New-Object 'System.Collections.Generic.List[string]'
        $type = $null
        for ($r = 0; $r -lt $tokSets.Count; $r++) {
            $row = $tokSets[$r]; $tk = $row[$p]
            if ($null -eq $type) { $type = [string]$tk['Type'] }
            [void]$vals.Add([string]$tk['Text'])
        }
        $valsArr = $vals.ToArray()
        $uniq = @($valsArr | Sort-Object -Unique)
        if ($uniq.Count -eq 1) {
            [void]$sb.Append($valsArr[0])
        } elseif ($type -eq 'sep') {
            # Whitespace-only sep variations: keep first variant, no symbol.
            $allWs = $true
            foreach ($v in $valsArr) { if ($v -match '\S') { $allWs = $false; break } }
            # Same-after-trim: drop the difference too (e.g. " {", "{", "{").
            $trimmed = @($valsArr | ForEach-Object { $_.Trim() } | Sort-Object -Unique)
            if ($allWs -or $trimmed.Count -le 1) { [void]$sb.Append($valsArr[0]) }
            else {
                $alloc = Allocate-Symbol -Values $valsArr -Kind 'sep'
                [void]$sb.Append("$($alloc.Pre)\$($alloc.Name)\$($alloc.Suf)")
            }
        } else {
            $alloc = Allocate-Symbol -Values $valsArr -Kind 'tok'
            [void]$sb.Append("$($alloc.Pre)\$($alloc.Name)\$($alloc.Suf)")
        }
    }
    return $sb.ToString()
}
#endregion

#region output helpers ---------------------------------------------------------
function CsvEscape {
    param([string]$s)
    if ($null -eq $s) { return '' }
    if ($s -match '[",\r\n]') { return '"' + ($s -replace '"','""') + '"' }
    return $s
}

function Write-FileWithRetry {
    # Tolerate transient read locks (editor with the file open).
    param([string]$Path, [string]$Content, [int]$Retries = 4)
    for ($k = 1; $k -le $Retries; $k++) {
        try { [IO.File]::WriteAllText($Path, $Content); return }
        catch [IO.IOException] {
            if ($k -eq $Retries) { break }
            Start-Sleep -Milliseconds (200 * $k)
        }
    }
    $tmp = "$Path.new"
    [IO.File]::WriteAllText($tmp, $Content)
    Write-Warning "Could not write $Path (locked); wrote $tmp instead."
}
#endregion

#region emit BP from aligned columns --------------------------------------------
$bpSb = [System.Text.StringBuilder]::new()
[void]$bpSb.AppendLine("# Cross-flow aligned BluePrint (v2)")
[void]$bpSb.AppendLine("# Source : $InputMtpl")
[void]$bpSb.AppendLine("# Flows  : $($Flows -join ', ')")
[void]$bpSb.AppendLine("# N      : $N")
[void]$bpSb.AppendLine("# Notes  : __BIN__/__CTR__/__BNUM__/__BYPASS__ placeholders are restored from $sliceName.binmap.json")
[void]$bpSb.AppendLine('')

$litCols = 0; $diffCols = 0; $gapCols = 0
$colIdx = 0
foreach ($col in $alignment) {
    $colIdx++
    try {
        $vals = @($col)
        $presentCount = 0
        foreach ($v in $vals) { if ($null -ne $v) { $presentCount++ } }
        if ($presentCount -eq 0) { continue }
        if ($presentCount -lt $N) {
            # Whole-line presence/absence column. Emit the FIRST non-empty
            # flow's literal line so the BP stays valid mtpl-shaped (no \Sn\
            # standalone placeholders that would block a build). The fact
            # that some flows omit this line is intentionally lossy here --
            # a downstream "expand to flow X" tool would reconstruct it from
            # per-flow stream files if precision were needed.
            $gapCols++
            $firstPresent = $null
            foreach ($v in $vals) { if ($null -ne $v -and $v -ne '') { $firstPresent = [string]$v; break } }
            if ($null -ne $firstPresent) { [void]$bpSb.AppendLine($firstPresent) }
            continue
        }
        $allEqual = $true
        for ($v = 1; $v -lt $vals.Count; $v++) {
            if ($vals[$v] -cne $vals[0]) { $allEqual = $false; break }
        }
        if ($allEqual) {
            $litCols++
            [void]$bpSb.AppendLine([string]$vals[0])
        } else {
            $diffCols++
            $strVals = New-Object 'System.Collections.Generic.List[string]'
            foreach ($v in $vals) { [void]$strVals.Add([string]$v) }
            [void]$bpSb.AppendLine((Render-DiffLine -Lines $strVals.ToArray()))
        }
    } catch {
        Write-Host "ERROR at column $colIdx : $_" -ForegroundColor Red
        Write-Host "  col contents: $($col -join ' || ')" -ForegroundColor Red
        throw
    }
}

# Initial BP write — may be replaced after derivation rewrite below
$bpInitial = $bpSb.ToString()
Write-Host "  BP written : $bpFile"
Write-Host "    literal columns : $litCols"
Write-Host "    diff columns    : $diffCols"
Write-Host "    gap columns     : $gapCols"
Write-Host "    symbols total   : $($script:symbols.Count)"
#endregion

#region derivation pass (learning 23) — DETECT, then APPLY ---------------------
# Step 1: scan all ordered (derived, base) pairs and collect candidates.
$candidatesByDerived = @{}
for ($ai = 0; $ai -lt $script:symbols.Count; $ai++) {
    for ($bi = 0; $bi -lt $script:symbols.Count; $bi++) {
        if ($ai -eq $bi) { continue }
        $symA = $script:symbols[$ai]; $symB = $script:symbols[$bi]
        if ($symA.Full.Count -ne $symB.Full.Count) { continue }
        $okAll = $true
        $pres = New-Object 'System.Collections.Generic.List[string]'
        $sufs = New-Object 'System.Collections.Generic.List[string]'
        for ($k = 0; $k -lt $symA.Full.Count; $k++) {
            $av = [string]$symA.Full[$k]; $bv = [string]$symB.Full[$k]
            if (-not $bv) { $okAll = $false; break }
            $idx = $av.IndexOf($bv)
            if ($idx -lt 0) { $okAll = $false; break }
            [void]$pres.Add($av.Substring(0, $idx))
            [void]$sufs.Add($av.Substring($idx + $bv.Length))
        }
        if (-not $okAll) { continue }
        $uPre = @($pres | Sort-Object -Unique)
        $uSuf = @($sufs | Sort-Object -Unique)
        if ($uPre.Count -eq 1 -and $uSuf.Count -eq 1 -and ($uPre[0] -ne '' -or $uSuf[0] -ne '')) {
            if (-not $candidatesByDerived.ContainsKey($symA.Name)) {
                $candidatesByDerived[$symA.Name] = New-Object 'System.Collections.Generic.List[hashtable]'
            }
            [void]$candidatesByDerived[$symA.Name].Add(@{ Base = $symB.Name; Pre = $uPre[0]; Suf = $uSuf[0] })
        }
    }
}

# Step 2: pick a preferred base per derived symbol. Preference order:
#   (1) vocab-named base (recognized name like FREQ_CORNER -- not S<n>)
#   (2) shortest base Full[0] length (most "atomic")
#   (3) first encountered
$symByName = @{}
foreach ($sym in $script:symbols) { $symByName[$sym.Name] = $sym }

$prefBase = @{}
foreach ($k in $candidatesByDerived.Keys) {
    $cands = $candidatesByDerived[$k]
    $vocabCand = $cands | Where-Object { $_.Base -notmatch '^S\d+$' } | Select-Object -First 1
    if ($vocabCand) { $prefBase[$k] = $vocabCand; continue }
    $best = $cands | Sort-Object { ([string]$symByName[$_.Base].Full[0]).Length } | Select-Object -First 1
    $prefBase[$k] = $best
}

# Step 3: drop edges that would create a cycle (e.g. A derived from B AND B
# derived from A would be inconsistent). Walk the chain; if we revisit a node
# already in-flight, drop the original edge.
$derivedSet = @{}
foreach ($k in $prefBase.Keys) { $derivedSet[$k] = $prefBase[$k] }

function Resolve-Chain {
    # Compose transitively: if base is itself derived, fold its pre/suf in
    # so the final mapping points to a root (non-derived) symbol.
    param([string]$Name, [hashtable]$Map)
    $visited = New-Object 'System.Collections.Generic.HashSet[string]'
    [void]$visited.Add($Name)
    $cur = $Map[$Name]
    $pre = $cur.Pre; $suf = $cur.Suf; $base = $cur.Base
    while ($Map.ContainsKey($base)) {
        if ($visited.Contains($base)) { return $null }   # cycle
        [void]$visited.Add($base)
        $next = $Map[$base]
        $pre = $pre + $next.Pre
        $suf = $next.Suf + $suf
        $base = $next.Base
    }
    return @{ Base = $base; Pre = $pre; Suf = $suf }
}

$resolved = @{}
foreach ($k in $derivedSet.Keys) {
    $r = Resolve-Chain -Name $k -Map $derivedSet
    if ($null -ne $r -and $r.Base -ne $k) { $resolved[$k] = $r }
}

# Step 4: rewrite BP. Replace each '\<derived>\' with '<pre>\<base>\<suf>'.
# Process longest-first to avoid prefix collisions (S1 vs S10).
$bpText = $bpInitial
$keysSorted = $resolved.Keys | Sort-Object { -$_.Length }
foreach ($d in $keysSorted) {
    $r = $resolved[$d]
    $bpText = $bpText.Replace("\$d\", "$($r.Pre)\$($r.Base)\$($r.Suf)")
}
Write-FileWithRetry -Path $bpFile -Content $bpText
Write-Host "  Derivations applied: $($resolved.Count) symbol(s) rewritten in BP"

# Step 5: log file
$derivLines = New-Object 'System.Collections.Generic.List[string]'
[void]$derivLines.Add("# Symbol derivation analysis (APPLIED)")
[void]$derivLines.Add("# Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm')")
[void]$derivLines.Add("# Format: <derived> -> <pre> + <base> + <suf>     (rewritten in BP, dropped from CSV)")
[void]$derivLines.Add("# Total applied: $($resolved.Count)")
[void]$derivLines.Add('')
foreach ($d in ($resolved.Keys | Sort-Object)) {
    $r = $resolved[$d]
    [void]$derivLines.Add("  $d -> '$($r.Pre)' + $($r.Base) + '$($r.Suf)'")
}
if ($candidatesByDerived.Count -gt $resolved.Count) {
    [void]$derivLines.Add('')
    [void]$derivLines.Add("# Skipped candidates (cycles or already-derived bases):")
    foreach ($k in ($candidatesByDerived.Keys | Sort-Object)) {
        if (-not $resolved.ContainsKey($k)) {
            foreach ($c in $candidatesByDerived[$k]) {
                [void]$derivLines.Add("  $k = '$($c.Pre)' + $($c.Base) + '$($c.Suf)'")
            }
        }
    }
}
Write-FileWithRetry -Path $derivFile -Content (($derivLines -join "`r`n") + "`r`n")
$derivCount = $resolved.Count
Write-Host "  Derivation log : $derivFile"
#endregion

#region emit symbols.csv (rows = symbols, cols = flows, cells = FULL values) --
$csvLines = New-Object 'System.Collections.Generic.List[string]'
$hdr = @('Symbol','Kind','Pre','Suf') + $Flows
[void]$csvLines.Add(($hdr | ForEach-Object { CsvEscape $_ }) -join ',')
$emittedCount = 0
foreach ($sym in $script:symbols) {
    if ($resolved.ContainsKey($sym.Name)) { continue }   # dropped: derived from another
    $row = @($sym.Name, $sym.Kind, $sym.Pre, $sym.Suf) + @($sym.Full)
    [void]$csvLines.Add(($row | ForEach-Object { CsvEscape $_ }) -join ',')
    $emittedCount++
}
Write-FileWithRetry -Path $csvFile -Content (($csvLines.ToArray() -join "`r`n") + "`r`n")
Write-Host "  CSV written: $csvFile  (rows=$emittedCount symbols, cols=$N flows + Pre/Suf, dropped=$($resolved.Count) derived)"
#endregion

#region emit binmap.json (learnings 25 + 1-4) ----------------------------------
$binJson = @{
    flows  = [ordered]@{}
    legend = @{
        bin    = '__BIN__   placeholder in BP -> per-flow original SetBin operands'
        ctr    = '__CTR__   placeholder in BP -> per-flow original IncrementCounters operands'
        bnum   = '__BNUM__  placeholder in BP -> per-flow original BaseNumbers value'
        bypass = '__BYPASS__ placeholder in BP -> per-flow original BypassPort value'
    }
}
foreach ($f in $Flows) {
    $list = New-Object 'System.Collections.Generic.List[object]'
    foreach ($e in $binmap[$f]) {
        [void]$list.Add(@{ kind = $e.Kind; value = $e.Value })
    }
    $binJson.flows[$f] = $list
}
$binJson | ConvertTo-Json -Depth 6 -Compress | Set-Content -Path $binFile -Encoding UTF8
Write-Host "  Binmap written: $binFile"
#endregion

#region log file ---------------------------------------------------------------
$logSb = [System.Text.StringBuilder]::new()
[void]$logSb.AppendLine("Cross-flow Aligned BluePrint Generator (v2)")
[void]$logSb.AppendLine("Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')")
[void]$logSb.AppendLine("Source   : $InputMtpl")
[void]$logSb.AppendLine("Flows    : $($Flows -join ', ')")
[void]$logSb.AppendLine("FlowsOnly: $FlowsOnly")
$cfgDisp = if ($ConfigFile) { $ConfigFile } else { '(none)' }
[void]$logSb.AppendLine("Vocab    : $($vocab.Count) symbols loaded from $cfgDisp")
[void]$logSb.AppendLine('')
[void]$logSb.AppendLine("Stream sizes:")
for ($s = 0; $s -lt $streams.Count; $s++) {
    [void]$logSb.AppendLine(("  {0,-30} -> {1,5} lines, {2,3} binmap entries" -f $Flows[$s], $streams[$s].Count, $binmap[$Flows[$s]].Count))
}
[void]$logSb.AppendLine('')
[void]$logSb.AppendLine("Aligned columns: $($alignment.Count)")
[void]$logSb.AppendLine("  literal : $litCols")
[void]$logSb.AppendLine("  diff    : $diffCols")
[void]$logSb.AppendLine("  gap     : $gapCols")
[void]$logSb.AppendLine("Symbols   : $($script:symbols.Count)")
[void]$logSb.AppendLine("Derivations: $derivCount (see $sliceName.derivations.log)")
Write-FileWithRetry -Path $logFile -Content $logSb.ToString()
#endregion

Write-Host ""
Write-Host "=== Done ==="
