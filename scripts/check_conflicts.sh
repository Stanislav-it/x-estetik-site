#!/usr/bin/env bash
set -euo pipefail

# Check for unresolved Git merge/rebase conflict markers.
# Returns non-zero if any markers are found.

if grep -R -n -F "<<<<<<<" . >/dev/null 2>&1 || grep -R -n -F ">>>>>>>" . >/dev/null 2>&1 || grep -R -n -F "=======" . >/dev/null 2>&1; then
  echo "ERROR: merge conflict markers found. Fix them before commit/deploy:"
  grep -R -n -F "<<<<<<<" . || true
  grep -R -n -F ">>>>>>>" . || true
  grep -R -n -F "=======" . || true
  exit 1
fi

echo "OK: no conflict markers found."
