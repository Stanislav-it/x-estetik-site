# Check for unresolved Git merge/rebase conflict markers.
$patterns = @('<<<<<<<', '=======', '>>>>>>>')
$hits = @()
Get-ChildItem -Recurse -File | ForEach-Object {
  try {
    $content = Get-Content -LiteralPath $_.FullName -Raw -ErrorAction Stop
    foreach ($p in $patterns) {
      if ($content -like "*$p*") {
        $hits += $_.FullName
        break
      }
    }
  } catch {
    # ignore binary / unreadable files
  }
}

if ($hits.Count -gt 0) {
  Write-Host "ERROR: merge conflict markers found in:" -ForegroundColor Red
  $hits | Sort-Object -Unique | ForEach-Object { Write-Host " - $_" }
  exit 1
}

Write-Host "OK: no conflict markers found." -ForegroundColor Green
