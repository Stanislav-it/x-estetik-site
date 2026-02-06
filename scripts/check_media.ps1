# Print expected media paths and report missing files.
# Run: powershell -ExecutionPolicy Bypass -File scripts\check_media.ps1

$expectedPhotos = @(
"DepiMax.JPEG",
"EMS FormaX.JPEG",
"Estetik Frax.JPEG",
"Lumera Estetik.JPEG",
"Regen Lift.JPEG",
"X-Blue Pen.JPEG",
"X-BOSS.JPEG",
"X-Contour KRIO.JPEG",
"X-Derma.JPEG",
"X-FRAXEL PRO.JPEG",
"X-FRAXEL.JPEG",
"X-Hair.JPEG",
"X-Levage Erbo.JPEG",
"X-Levage Pro.JPEG",
"X-Shape.JPEG",
"X-V980.JPEG"
)

$expectedVideoBases = @(
"video 1",
"video 2",
"video 3",
"video 4",
"video 5",
"video 6",
"video 7",
"video 8",
"video 9",
"video 10",
"video 11",
"video 12",
"video 13",
"video 14",
"video 15",
"video 16",
"video 17",
"video 18",
"video 19",
"video 20",
"video 21",
"video 22",
)

Write-Host "PHOTOS (static/photos):"
foreach ($f in $expectedPhotos) {
  $p = Join-Path "static\photos" $f
  if (Test-Path $p) { Write-Host " OK  $p" } else { Write-Host " MISSING  $p" }
}

Write-Host ""
Write-Host "VIDEOS (static/video):"
$exts = @(".mp4",".mov",".m4v",".webm",".MP4",".MOV",".M4V",".WEBM")
foreach ($b in $expectedVideoBases) {
  $found = $false
  foreach ($e in $exts) {
    $p = Join-Path "static\video" ($b + $e)
    if (Test-Path $p) { Write-Host " OK  $p"; $found=$true; break }
  }
  if (-not $found) { Write-Host " MISSING  static\video\$b.(mp4|mov|m4v|webm)" }
}
