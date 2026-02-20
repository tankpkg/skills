#!/usr/bin/env bash
#
# version-bump.sh - Bump version in skills.json
#
# Usage:
#   ./version-bump.sh [major|minor|patch] [directory]
#
# Arguments:
#   type      - Version bump type: major, minor, or patch (default: patch)
#   directory - Path to skill directory (default: current directory)
#
# Examples:
#   ./version-bump.sh patch    # 1.0.0 -> 1.0.1
#   ./version-bump.sh minor    # 1.0.0 -> 1.1.0
#   ./version-bump.sh major    # 1.0.0 -> 2.0.0
#

set -euo pipefail

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

BUMP_TYPE="${1:-patch}"
SKILL_DIR="${2:-.}"
MANIFEST="$SKILL_DIR/skills.json"

if [[ ! "$BUMP_TYPE" =~ ^(major|minor|patch)$ ]]; then
    echo "Error: Invalid bump type '$BUMP_TYPE'"
    echo "Usage: $0 [major|minor|patch] [directory]"
    exit 1
fi

if [[ ! -f "$MANIFEST" ]]; then
    echo "Error: skills.json not found in $SKILL_DIR"
    exit 1
fi

CURRENT=$(jq -r '.version' "$MANIFEST")

if [[ ! "$CURRENT" =~ ^[0-9]+\.[0-9]+\.[0-9]+ ]]; then
    echo "Error: Current version '$CURRENT' is not valid semver"
    exit 1
fi

MAJOR=$(echo "$CURRENT" | cut -d. -f1)
MINOR=$(echo "$CURRENT" | cut -d. -f2)
PATCH=$(echo "$CURRENT" | cut -d. -f3 | cut -d- -f1)

case "$BUMP_TYPE" in
    major)
        MAJOR=$((MAJOR + 1))
        MINOR=0
        PATCH=0
        ;;
    minor)
        MINOR=$((MINOR + 1))
        PATCH=0
        ;;
    patch)
        PATCH=$((PATCH + 1))
        ;;
esac

NEW_VERSION="$MAJOR.$MINOR.$PATCH"

jq --arg v "$NEW_VERSION" '.version = $v' "$MANIFEST" > "$MANIFEST.tmp"
mv "$MANIFEST.tmp" "$MANIFEST"

echo -e "${GREEN}Version bumped:${NC} $CURRENT -> $NEW_VERSION"

SKILL_MD="$SKILL_DIR/SKILL.md"
if [[ -f "$SKILL_MD" ]] && grep -q "^version:" "$SKILL_MD" 2>/dev/null; then
    sed -i.bak "s/^version:.*$/version: \"$NEW_VERSION\"/" "$SKILL_MD"
    rm -f "$SKILL_MD.bak"
    echo -e "${GREEN}Updated SKILL.md version${NC}"
fi

echo
echo -e "${YELLOW}Reminder:${NC} Update your changelog with changes for $NEW_VERSION"
echo "  git add $MANIFEST"
echo "  git commit -m \"chore: bump version to $NEW_VERSION\""
