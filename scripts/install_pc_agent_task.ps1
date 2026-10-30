# ARIA PC Agent — Windows Task Scheduler Registration
# Run this script ONCE as Administrator to install the 5-minute scheduled task.
# After installation, ARIA PC Agent runs every 5 minutes automatically.
# Task exits cleanly after each run — no background process stays alive.

param(
    [string]$PythonPath = "python",
    [string]$AgentRoot  = "D:\aria-agent"
)

$AgentScript = Join-Path $AgentRoot "daemon\aria_pc_agent.py"
$TaskName    = "ARIA_PC_Agent"
$LogFile     = Join-Path $AgentRoot "data\pc_agent.log"

Write-Host "Installing ARIA PC Agent as Windows Scheduled Task..." -ForegroundColor Cyan

# Check Python
try {
    $v = & $PythonPath --version 2>&1
    Write-Host "Python: $v" -ForegroundColor Green
} catch {
    Write-Error "Python not found at: $PythonPath. Pass -PythonPath to specify."
    exit 1
}

# Check script exists
if (-not (Test-Path $AgentScript)) {
    Write-Error "Agent script not found: $AgentScript"
    exit 1
}

# Remove existing task if present
Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue

# Build action
$Action  = New-ScheduledTaskAction `
    -Execute $PythonPath `
    -Argument "`"$AgentScript`"" `
    -WorkingDirectory $AgentRoot

# Trigger: every 5 minutes, indefinitely
$Trigger = New-ScheduledTaskTrigger -RepetitionInterval (New-TimeSpan -Minutes 5) -Once -At (Get-Date)

# Settings: run even on battery, wake if needed, do not start new instance if already running
$Settings = New-ScheduledTaskSettingsSet `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 4) `
    -MultipleInstances IgnoreNew `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable:$false

# Principal: run as current user (no elevation needed for clipboard/health/screenshot)
$Principal = New-ScheduledTaskPrincipal `
    -UserId ([System.Security.Principal.WindowsIdentity]::GetCurrent().Name) `
    -LogonType Interactive `
    -RunLevel Limited

Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $Action `
    -Trigger $Trigger `
    -Settings $Settings `
    -Principal $Principal `
    -Description "ARIA PC Agent — clipboard watcher, health monitor, Telegram remote control" `
    -Force

Write-Host ""
Write-Host "✅ ARIA PC Agent installed successfully!" -ForegroundColor Green
Write-Host "   Task: $TaskName" -ForegroundColor Green
Write-Host "   Fires: every 5 minutes" -ForegroundColor Green
Write-Host "   Script: $AgentScript" -ForegroundColor Green
Write-Host ""
Write-Host ("To verify:  Get-ScheduledTask -TaskName '" + $TaskName + "'") -ForegroundColor Yellow
Write-Host ("To remove:  Unregister-ScheduledTask -TaskName '" + $TaskName + "' -Confirm:`$false") -ForegroundColor Yellow
Write-Host ("To run now: Start-ScheduledTask -TaskName '" + $TaskName + "'") -ForegroundColor Yellow
