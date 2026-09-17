# Bootstrap VpetFlutter platform shells when Flutter SDK is available.
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot\..

if (-not (Get-Command flutter -ErrorAction SilentlyContinue)) {
  Write-Host "Flutter not on PATH. Install Flutter then re-run."
  Write-Host "https://docs.flutter.dev/get-started/install/windows"
  exit 1
}

python tools/sync_assets.py
flutter create --org com.vpet.eiden --project-name vpet_eiden --platforms=android,ios .
flutter pub get
Write-Host "OK. Run: flutter run"
