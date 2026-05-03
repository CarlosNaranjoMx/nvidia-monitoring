# NVIDIA Monitoring Script

This repository contains a PowerShell monitoring script for NVIDIA GPUs, specifically tested with an NVIDIA GeForce RTX 4060 Ti.

## Files
- `nvidia_monitor.ps1`: PowerShell script that:
  - runs `nvidia-smi -q`
  - queries `Win32_VideoController` for NVIDIA GPU details
  - writes output to timestamped log files
  - removes the previous day's log file for the same time
  - removes logs older than 2 days

## Usage
1. Place the script in a directory such as `D:\resources_psycho\resources_github\repos_publicos\hardware\monitoreo`.
2. Run with PowerShell:
   ```powershell
   powershell.exe -NoProfile -ExecutionPolicy Bypass -File "D:\resources_psycho\resources_github\repos_publicos\hardware\monitoreo\nvidia_monitor.ps1"
   ```
3. Schedule it in Windows Task Scheduler to run every 5 minutes.

## Notes
- The script keeps only one log file per 5-minute interval for the last 24 hours.
- Logs older than 2 days are also cleaned up to avoid disk buildup.
