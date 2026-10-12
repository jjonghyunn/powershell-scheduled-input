[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)] [datetime]$At,
    [string]$Message,
    [string]$TextFile,
    [string]$WindowTitle,
    [string]$ProcessName,
    [int]$ActivationRetries = 10,
    [int]$RetryDelaySeconds = 1,
    [switch]$NoEnter
)

$ErrorActionPreference = 'Stop'
if ([string]::IsNullOrWhiteSpace($Message) -and [string]::IsNullOrWhiteSpace($TextFile)) { throw 'Specify either -Message or -TextFile.' }
if (-not [string]::IsNullOrWhiteSpace($Message) -and -not [string]::IsNullOrWhiteSpace($TextFile)) { throw 'Use only one of -Message and -TextFile.' }
if ([string]::IsNullOrWhiteSpace($WindowTitle) -and [string]::IsNullOrWhiteSpace($ProcessName)) { throw 'Specify -WindowTitle or -ProcessName.' }
if (-not [string]::IsNullOrWhiteSpace($WindowTitle) -and -not [string]::IsNullOrWhiteSpace($ProcessName)) { throw 'Use only one of -WindowTitle and -ProcessName.' }
if ($ActivationRetries -lt 1) { throw '-ActivationRetries must be at least 1.' }
if ($RetryDelaySeconds -lt 0) { throw '-RetryDelaySeconds cannot be negative.' }

if (-not [string]::IsNullOrWhiteSpace($TextFile)) {
    if (-not (Test-Path -LiteralPath $TextFile -PathType Leaf)) { throw "Text file not found: $TextFile" }
    $content = [System.IO.File]::ReadAllText((Resolve-Path -LiteralPath $TextFile).Path)
} else { $content = $Message }
if ([string]::IsNullOrEmpty($content)) { throw 'The message is empty.' }

$now = Get-Date
if ($At -gt $now) {
    $wait = ($At - $now).TotalSeconds
    Write-Host ("Waiting until {0} ({1:N1} seconds)..." -f $At.ToString('yyyy-MM-dd HH:mm:ss'), $wait)
    Start-Sleep -Seconds ([math]::Ceiling($wait))
}

$shell = New-Object -ComObject WScript.Shell
$activated = $false
for ($attempt = 1; $attempt -le $ActivationRetries; $attempt++) {
    if (-not [string]::IsNullOrWhiteSpace($ProcessName)) {
        $process = Get-Process -Name $ProcessName -ErrorAction SilentlyContinue |
            Where-Object { $_.MainWindowHandle -ne 0 } | Select-Object -First 1
        if ($null -ne $process) { $activated = $shell.AppActivate($process.Id) }
    } else { $activated = $shell.AppActivate($WindowTitle) }
    if ($activated) { break }
    if ($attempt -lt $ActivationRetries) { Start-Sleep -Seconds $RetryDelaySeconds }
}
if (-not $activated) { throw 'Could not activate the target window. Check the target parameters and that the window is visible.' }

# Clipboard paste preserves Unicode and newlines without SendKeys escaping.
Add-Type -AssemblyName System.Windows.Forms
$oldClipboard = $null
$hadTextClipboard = $false
try {
    try { $oldClipboard = [System.Windows.Forms.Clipboard]::GetText(); $hadTextClipboard = $true } catch { }
    [System.Windows.Forms.Clipboard]::SetText($content)
    Start-Sleep -Milliseconds 150
    $shell.SendKeys('^v')
    if (-not $NoEnter) { Start-Sleep -Milliseconds 100; $shell.SendKeys('{ENTER}') }
} finally {
    if ($hadTextClipboard) { try { [System.Windows.Forms.Clipboard]::SetText($oldClipboard) } catch { } }
}
Write-Host ("Sent {0} characters to the target window{1}." -f $content.Length, $(if ($NoEnter) { '' } else { ' and pressed Enter' }))
