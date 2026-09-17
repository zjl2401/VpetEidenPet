# Eiden hot-reload launcher (called by start_eiden.bat / .vbs)
$ErrorActionPreference = 'SilentlyContinue'
$AppDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Src = 'C:\Users\36255\Desktop\VpetEidenPet'
$Lnk = Join-Path ([Environment]::GetFolderPath('Desktop')) 'Vpet Eiden.lnk'
$Vbs = Join-Path $AppDir 'start_eiden.vbs'

Write-Host "[Eiden] prefer source launch from $Src"

# Kill old Eiden only
Get-CimInstance Win32_Process -EA SilentlyContinue | Where-Object {
  $_.ExecutablePath -like '*\VpetEidenApp\Vpet.exe' -or
  $_.CommandLine -like '*VpetEidenPet*vpet_app.py*'
} | ForEach-Object {
  Stop-Process -Id $_.ProcessId -Force -EA SilentlyContinue
}
Start-Sleep -Milliseconds 800

# Sync sidecars for exe fallback
$internal = Join-Path $AppDir '_internal'
if (Test-Path (Join-Path $Src 'pet.py')) {
  New-Item -ItemType Directory -Force -Path $internal | Out-Null
  foreach ($name in @(
    'pet.py','vpet_app.py','vpet_launcher.py','peer_friendship.py',
    'system_media_control.py','pet_outfit.py','app_scene_desktop.py',
    'owner_bond.py','companion_quotes.py','emote_registry.py','character_profile.py'
  )) {
    $from = Join-Path $Src $name
    if (Test-Path $from) {
      Copy-Item $from (Join-Path $internal $name) -Force
    }
  }
  Set-Content -Path (Join-Path $internal 'HOT_RELOAD_STAMP.txt') -Value ("synced " + (Get-Date)) -Encoding UTF8
}

# Launch tray once (spawn_on_launcher_start -> one pet). Avoid cmd START (breaks under VBS).
$launched = $false
$pyw = Get-Command pythonw -EA SilentlyContinue
if (-not $pyw) { $pyw = Get-Command python -EA SilentlyContinue }
if ($pyw -and (Test-Path (Join-Path $Src 'vpet_app.py'))) {
  Start-Process -FilePath $pyw.Source -ArgumentList @((Join-Path $Src 'vpet_app.py')) -WorkingDirectory $Src
  Write-Host ("[Eiden] launched " + $pyw.Source)
  $launched = $true
} elseif (Test-Path (Join-Path $AppDir 'Vpet.exe')) {
  Start-Process -FilePath (Join-Path $AppDir 'Vpet.exe') -WorkingDirectory $AppDir
  Write-Host '[Eiden] fallback Vpet.exe'
  $launched = $true
}

# Pin desktop shortcut to hot-reload VBS
try {
  $wsh = New-Object -ComObject WScript.Shell
  $sc = $wsh.CreateShortcut($Lnk)
  $sc.TargetPath = $Vbs
  $sc.WorkingDirectory = $AppDir
  $sc.Arguments = ''
  $sc.WindowStyle = 1
  $sc.Description = 'Vpet Eiden hot-reload'
  $ico = Join-Path $AppDir 'app_icon.ico'
  if (Test-Path $ico) { $sc.IconLocation = "$ico,0" }
  $sc.Save()
} catch {}

if (-not $launched) {
  Write-Host '[Eiden] launch failed: no python / Vpet.exe'
  exit 1
}
exit 0
