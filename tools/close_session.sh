#!/usr/bin/env bash
# close_session.sh — residual manual steps Claude cannot autorun
#
# Claude completed the in-repo work for v0.1.3 (code, tests, CI, tag push) but a few
# steps need user-side credentials that Claude is forbidden from handling (R11):
#   1. GitHub Release object creation (gh release create requires gh auth token in process)
#   2. Optional PyPI upload (requires PYPI_API_TOKEN)
#
# Run this script from the repo root with `bash tools/close_session.sh` after Claude
# finishes. The script is idempotent: re-running it skips already-completed steps.
#
# Prerequisites:
#   - gh CLI installed and authenticated (`gh auth status` should succeed)
#   - Repo cloned with tag v0.1.3 present locally (auto-fetched if missing)
#   - dist/ directory contains machinic_assemblage-0.1.3-*.whl and *.tar.gz (rebuilt below)
#
# What this script does:
#   - Re-validates the working tree, tags, and dist artifacts
#   - Creates GitHub Release objects for v0.1.0, v0.1.1, v0.1.2, v0.1.3 (if missing)
#     - Attaches dist/*-0.1.3* to v0.1.3 (the latest, current build)
#     - Older tags get Release-only entries without attached artifacts
#     - Release notes for each version are pulled from CHANGELOG.md
#   - (OPTIONAL) Uploads v0.1.3 wheel+sdist to PyPI if PYPI_API_TOKEN is set
#
# Re-run safety:
#   - `gh release create` is replaced by an existence check so re-running is a no-op
#   - `python -m build` only re-runs if dist/*0.1.3* is missing
#   - The script never deletes or amends prior releases

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

err() { printf '[close_session] ERROR: %s\n' "$*" >&2; exit 1; }
note() { printf '[close_session] %s\n' "$*"; }

# ---- 0. Sanity checks ----------------------------------------------------------------------
command -v gh >/dev/null 2>&1 || err "gh CLI not installed. https://cli.github.com/"
gh auth status >/dev/null 2>&1 || err "gh not authenticated. Run: gh auth login"

if [ "$(git rev-parse --abbrev-ref HEAD 2>/dev/null)" != "main" ]; then
  note "warning: not on main branch — current = $(git rev-parse --abbrev-ref HEAD)"
fi

# ---- 1. Ensure dist/ has v0.1.3 artifacts --------------------------------------------------
WHL="dist/machinic_assemblage-0.1.3-py3-none-any.whl"
SDIST="dist/machinic_assemblage-0.1.3.tar.gz"

if [ ! -f "$WHL" ] || [ ! -f "$SDIST" ]; then
  note "Building v0.1.3 wheel + sdist (python -m build)..."
  command -v python3 >/dev/null 2>&1 || err "python3 not installed"
  python3 -m pip show build >/dev/null 2>&1 || python3 -m pip install --user build
  rm -f dist/machinic_assemblage-0.1.3*  # safe: only v0.1.3 artifacts
  python3 -m build
fi

[ -f "$WHL" ] || err "wheel still missing after build: $WHL"
[ -f "$SDIST" ] || err "sdist still missing after build: $SDIST"

# ---- 2. Verify tags exist locally and on origin --------------------------------------------
for tag in v0.1.0 v0.1.1 v0.1.2 v0.1.3; do
  if ! git rev-parse --verify "$tag" >/dev/null 2>&1; then
    note "fetching missing local tag $tag..."
    git fetch origin "refs/tags/$tag:refs/tags/$tag"
  fi
done

# ---- 3. Extract release notes per version from CHANGELOG.md --------------------------------
# Each section is `## [X.Y.Z] — date` … up to the next `## [` line.
extract_notes() {
  local version="$1"
  awk -v ver="$version" '
    BEGIN { in_section = 0 }
    /^## \[/ {
      if (in_section) exit
      if ($0 ~ "^## \\[" ver "\\]") { in_section = 1; next }
    }
    in_section { print }
  ' CHANGELOG.md
}

# ---- 4. Create GitHub Release for each version (idempotent) --------------------------------
release_exists() {
  gh release view "$1" --json tagName >/dev/null 2>&1
}

create_release() {
  local tag="$1"
  shift  # remaining args are artifact paths
  if release_exists "$tag"; then
    note "release $tag already exists — skipping"
    return 0
  fi
  local notes_file
  notes_file="$(mktemp)"
  trap 'rm -f "$notes_file"' RETURN
  extract_notes "$tag" >"$notes_file"
  if [ ! -s "$notes_file" ]; then
    note "warning: no CHANGELOG section found for $tag; using a fallback note"
    printf '%s release. See [CHANGELOG.md](CHANGELOG.md) for details.\n' "$tag" >"$notes_file"
  fi
  note "creating release $tag with $# artifact(s)..."
  if [ "$#" -gt 0 ]; then
    gh release create "$tag" "$@" --title "$tag" --notes-file "$notes_file" --verify-tag
  else
    gh release create "$tag" --title "$tag" --notes-file "$notes_file" --verify-tag
  fi
  rm -f "$notes_file"
  trap - RETURN
}

create_release v0.1.0
create_release v0.1.1
create_release v0.1.2
create_release v0.1.3 "$WHL" "$SDIST"

# ---- 5. (OPTIONAL) PyPI upload --------------------------------------------------------------
# Set PYPI_API_TOKEN in your environment to enable. Skip by default.
if [ -n "${PYPI_API_TOKEN:-}" ]; then
  note "PYPI_API_TOKEN detected — uploading v0.1.3 to PyPI..."
  python3 -m pip show twine >/dev/null 2>&1 || python3 -m pip install --user twine
  TWINE_USERNAME="__token__" TWINE_PASSWORD="$PYPI_API_TOKEN" \
    python3 -m twine upload --non-interactive "$WHL" "$SDIST"
  note "PyPI upload complete."
else
  note "PYPI_API_TOKEN not set — skipping PyPI upload (intentional). Set the env var to enable."
fi

# ---- 6. Summary -----------------------------------------------------------------------------
note "done. Releases:"
gh release list --limit 5

note "Repo state:"
git log --oneline -5
git tag -l "v0.1.*"
