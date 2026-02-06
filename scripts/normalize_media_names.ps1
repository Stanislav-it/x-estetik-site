# Normalize media filenames to be URL-safe and consistent (fix "fancy" dashes, NBSP, double spaces).
# Run from repo root: powershell -ExecutionPolicy Bypass -File scripts\normalize_media_names.ps1

$folders = @("static\photos", "static\video")

function Normalize-Name([string]$name) {
  # Convert various hyphens/dashes to ASCII '-'
  $name = $name -replace "[‐‑‒–—−`u2011]", "-"
  # Convert NBSP to space
  $name = $name -replace ([char]0x00A0), " "
  # Collapse multiple spaces
  $name = ($name -replace "\s+", " ").Trim()
  return $name
}

foreach ($folder in $folders) {
  if (!(Test-Path $folder)) { continue }
  Get-ChildItem $folder -File | ForEach-Object {
    $old = $_.Name
    $new = Normalize-Name $old
    if ($new -ne $old) {
      Rename-Item $_.FullName -NewName $new
      Write-Host "RENAMED: $old -> $new"
    }
  }
}

Write-Host "Done."
