# Compress videos to fit GitHub (no LFS). GitHub limit is 100MB per file (recommended <= 95MB).
# Requires ffmpeg + ffprobe in PATH.
# Run from repo root: powershell -ExecutionPolicy Bypass -File scripts\compress_videos_for_github.ps1

$targetMB = 95
$audioKbps = 128
$inDir = "static\video"
$outDir = "static\video_compressed"

if (!(Test-Path $inDir)) { Write-Host "No $inDir folder."; exit 1 }
New-Item -ItemType Directory -Force -Path $outDir | Out-Null

function Get-DurationSec([string]$file) {
  $dur = & ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 "$file"
  return [double]$dur
}

Get-ChildItem $inDir -File | Where-Object { $_.Extension -match "^\.(mp4|mov|m4v|webm)$" } | ForEach-Object {
  $src = $_.FullName
  $dur = Get-DurationSec $src
  if ($dur -le 0) { Write-Host "Skip (no duration): $($_.Name)"; return }

  # Total bitrate budget (kbps) = sizeMB * 8192 / seconds
  $totalKbps = [math]::Floor(($targetMB * 8192) / $dur)
  $videoKbps = [math]::Max(300, $totalKbps - $audioKbps)

  $dst = Join-Path $outDir ($_.BaseName + ".mp4")
  Write-Host ("Encoding {0} -> {1} (dur {2:n1}s, v={3}kbps, a={4}kbps)" -f $_.Name, (Split-Path $dst -Leaf), $dur, $videoKbps, $audioKbps)

  & ffmpeg -y -i "$src" `
    -c:v libx264 -preset medium -b:v "${videoKbps}k" -maxrate "${videoKbps}k" -bufsize "${videoKbps}k" -pix_fmt yuv420p `
    -c:a aac -b:a "${audioKbps}k" `
    -movflags +faststart `
    "$dst" | Out-Host
}

Write-Host "Done. Check files in $outDir and replace originals if quality is OK."
