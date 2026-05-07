# _common.ps1 - Shared helpers for all PTLP Trace API skills
# Dot-source this file at the top of each skill's PS1 wrapper:
#   . "$PSScriptRoot\_common.ps1"

$script:UsageLogPath    = "\\ger.corp.intel.com\ec\proj\mdl\ha\intel\engineering\dev\user_links\yrakotch\LLM\CODE\Usage\usage_log.csv"
$script:FeedbackLogPath = "\\ger.corp.intel.com\ec\proj\mdl\ha\intel\engineering\dev\user_links\yrakotch\LLM\CODE\Usage\feedback_log.csv"
$script:UsageLogHeaders    = "Timestamp,User,MachineName,SkillName,Site,Lot,Operation,Socket,ExitCode,DurationSec"
$script:FeedbackLogHeaders = "Timestamp,User,SkillName,Lot,Operation,Rating,Comment"

function Write-UsageLog {
    param(
        [string]$SkillName,
        [string]$Lot        = "",
        [string]$Operation  = "",
        [string]$Socket     = "",
        [string]$Site       = "",
        [int]$ExitCode      = 0,
        [double]$DurationSec = 0
    )
    try {
        $ts  = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
        $row = "$ts,$env:USERNAME,$env:COMPUTERNAME,$SkillName,$Site,$Lot,$Operation,$Socket,$ExitCode,$([math]::Round($DurationSec,1))"
        if (-not (Test-Path $script:UsageLogPath)) {
            $script:UsageLogHeaders | Out-File -FilePath $script:UsageLogPath -Encoding utf8 -ErrorAction Stop
        }
        $row | Out-File -FilePath $script:UsageLogPath -Append -Encoding utf8 -ErrorAction Stop
    }
    catch {
        # Non-fatal: silently ignore if network log is unavailable
    }
}

function Request-Feedback {
    param(
        [string]$SkillName,
        [string]$Lot       = "",
        [string]$Operation = "",
        [string]$Socket    = "",
        [switch]$Skip
    )
    if ($Skip) { return }
    try {
        # If stdin is redirected (CI / pipe / non-interactive) skip silently
        if ([Console]::IsInputRedirected) { return }

        $timeout = 12   # seconds before auto-skip

        Write-Host ""
        Write-Host "--- Feedback (optional, auto-skip in ${timeout}s) ---" -ForegroundColor DarkGray
        Write-Host "Rate this output [1=Poor 2=Fair 3=Good 4=Great 5=Excellent, any other key = skip]: " -NoNewline -ForegroundColor DarkGray

        $rating = ""
        $sw = [System.Diagnostics.Stopwatch]::StartNew()
        while ($sw.Elapsed.TotalSeconds -lt $timeout) {
            if ([Console]::KeyAvailable) {
                $key = [Console]::ReadKey($true)
                if ($key.KeyChar -match '^[1-5]$') {
                    $rating = [string]$key.KeyChar
                    Write-Host $rating
                } else {
                    Write-Host "(skipped)"
                }
                break
            }
            Start-Sleep -Milliseconds 150
        }
        # Timed out without a key press
        if (-not $rating -and $sw.Elapsed.TotalSeconds -ge $timeout) {
            Write-Host "(auto-skipped)" -ForegroundColor DarkGray
        }

        if ($rating) {
            Write-Host "Short comment (Enter to skip): " -NoNewline -ForegroundColor DarkGray
            $comment = (Read-Host) -replace ',', ';'
            $ts  = Get-Date -Format "yyyy-MM-ddTHH:mm:ss"
            $row = "$ts,$env:USERNAME,$SkillName,$Lot,$Operation,$rating,$comment"
            if (-not (Test-Path $script:FeedbackLogPath)) {
                $script:FeedbackLogHeaders | Out-File -FilePath $script:FeedbackLogPath -Encoding utf8 -ErrorAction Stop
            }
            $row | Out-File -FilePath $script:FeedbackLogPath -Append -Encoding utf8 -ErrorAction Stop
            Write-Host "Thank you!" -ForegroundColor Green
        }
    }
    catch {
        # Non-fatal: silently ignore all errors (including non-interactive console exceptions)
    }
}
