# Set this to the actual directory before running the script.
$logDir = '<DIRECTORY>'
if (-not (Test-Path $logDir)) { New-Item -Path $logDir -ItemType Directory -Force | Out-Null }

$now = Get-Date
$timestamp = $now.ToString('yyyyMMdd_HHmm')
$logFile = Join-Path $logDir "03_nvidia_$timestamp.txt"
$prevLogFile = Join-Path $logDir "03_nvidia_$($now.AddDays(-1).ToString('yyyyMMdd_HHmm')).txt"

$report = @()
$report += "Timestamp: $($now.ToString('yyyy-MM-dd HH:mm:ss'))"
$report += ""
$report += "=== nvidia-smi -q ==="
try {
    $report += (nvidia-smi -q | Out-String -Width 4096)
} catch {
    $report += "ERROR: nvidia-smi failed: $($_.Exception.Message)"
}
$report += ""
$report += "=== Win32_VideoController ==="
try {
    $report += (Get-CimInstance Win32_VideoController | Where-Object Name -like '*NVIDIA*' | Select-Object Name, DriverVersion, DriverDate, VideoProcessor, AdapterRAM, PNPDeviceID | Format-List | Out-String -Width 4096)
} catch {
    $report += "ERROR: Win32_VideoController query failed: $($_.Exception.Message)"
}
$report += ""
$report += "=== Retention cleanup ==="
if (Test-Path $prevLogFile) {
    try {
        Remove-Item -Path $prevLogFile -ErrorAction Stop
        $report += "Deleted old log: $prevLogFile"
    } catch {
        $report += "ERROR deleting old log: $($_.Exception.Message)"
    }
} else {
    $report += "No log found to delete for previous day same time: $prevLogFile"
}

# Conservative cleanup: remove any file older than 2 days
try {
    Get-ChildItem -Path $logDir -Filter '03_nvidia_*.txt' | Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-2) } | ForEach-Object {
        Remove-Item -Path $_.FullName -ErrorAction Stop
        $report += "Removed aged log: $($_.FullName)"
    }
} catch {
    $report += "ERROR cleaning aged logs: $($_.Exception.Message)"
}

$report | Out-File -FilePath $logFile -Encoding utf8 -Force
