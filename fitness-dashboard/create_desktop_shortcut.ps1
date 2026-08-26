# PowerShell script to create Desktop shortcut for Fitness Dashboard
$WshShell = New-Object -ComObject WScript.Shell

$ProjectDir = "D:\My fitness\fitness-dashboard"
$TargetVbs = Join-Path $ProjectDir "Fitness Dashboard (Silent).vbs"
$TargetBat = Join-Path $ProjectDir "Fitness Dashboard.bat"

# Detect desktop paths (Standard and OneDrive Desktop)
$DesktopPaths = @(
    [Environment]::GetFolderPath("Desktop"),
    "C:\Users\ranit\OneDrive\Desktop",
    "C:\Users\ranit\Desktop"
) | Select-Object -Unique

foreach ($Desktop in $DesktopPaths) {
    if (Test-Path $Desktop) {
        $ShortcutPath = Join-Path $Desktop "Fitness Dashboard.lnk"
        $Shortcut = $WshShell.CreateShortcut($ShortcutPath)
        $Shortcut.TargetPath = "wscript.exe"
        $Shortcut.Arguments = "`"$TargetVbs`""
        $Shortcut.WorkingDirectory = $ProjectDir
        $Shortcut.Description = "Launch My Fitness Dashboard"
        $Shortcut.IconLocation = "shell32.dll,238"  # Globe / Web icon
        $Shortcut.Save()
        Write-Host "Created shortcut at: $ShortcutPath"
    }
}
