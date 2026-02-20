#!/usr/bin/env bash
#
# validate-manifest.sh - Validate skills.json against Tank schema
#
# Usage:
#   ./validate-manifest.sh [directory]
#
# Arguments:
#   directory - Path to skill directory (default: current directory)
#
# Exit codes:
#   0 - Valid manifest
#   1 - Missing or invalid manifest
#   2 - Schema validation failed
#

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

SKILL_DIR="${1:-.}"
MANIFEST="$SKILL_DIR/skills.json"

echo "Validating manifest: $MANIFEST"
echo

# Check file exists
if [[ ! -f "$MANIFEST" ]]; then
    echo -e "${RED}ERROR: skills.json not found${NC}"
    echo "Run 'tank init' to create a manifest"
    exit 1
fi

# Check JSON is valid
if ! jq empty "$MANIFEST" 2>/dev/null; then
    echo -e "${RED}ERROR: Invalid JSON syntax${NC}"
    echo "Run: cat skills.json | jq ."
    exit 1
fi

echo -e "${GREEN}✓${NC} JSON syntax valid"

# Extract fields
NAME=$(jq -r '.name // empty' "$MANIFEST")
VERSION=$(jq -r '.version // empty' "$MANIFEST")
DESCRIPTION=$(jq -r '.description // empty' "$MANIFEST")

# Validate required fields
ERRORS=0

if [[ -z "$NAME" ]]; then
    echo -e "${RED}✗${NC} Missing required field: name"
    ERRORS=$((ERRORS + 1))
else
    echo -e "${GREEN}✓${NC} name: $NAME"
fi

if [[ -z "$VERSION" ]]; then
    echo -e "${RED}✗${NC} Missing required field: version"
    ERRORS=$((ERRORS + 1))
else
    echo -e "${GREEN}✓${NC} version: $VERSION"
fi

# Validate name format
if [[ -n "$NAME" ]]; then
    if [[ ${#NAME} -gt 214 ]]; then
        echo -e "${RED}✗${NC} Name exceeds 214 characters"
        ERRORS=$((ERRORS + 1))
    fi
    
    if [[ ! "$NAME" =~ ^(@[a-z0-9-]+/)?[a-z0-9][a-z0-9-]*$ ]]; then
        echo -e "${RED}✗${NC} Invalid name format"
        echo "  Must be: lowercase letters, numbers, hyphens"
        echo "  Optional scope: @org/name"
        ERRORS=$((ERRORS + 1))
    fi
fi

# Validate version format
if [[ -n "$VERSION" ]]; then
    if [[ ! "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+(-[a-zA-Z0-9.]+)?(\+[a-zA-Z0-9.]+)?$ ]]; then
        echo -e "${RED}✗${NC} Invalid version format (must be semver: X.Y.Z)"
        ERRORS=$((ERRORS + 1))
    fi
fi

# Validate description length
if [[ -n "$DESCRIPTION" ]] && [[ ${#DESCRIPTION} -gt 500 ]]; then
    echo -e "${YELLOW}⚠${NC} Description exceeds 500 characters (${#DESCRIPTION})"
fi

# Validate permissions structure if present
if jq -e '.permissions' "$MANIFEST" > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} permissions defined"
    
    # Check for unknown permission types
    KNOWN_PERMS='["network", "filesystem", "subprocess"]'
    UNKNOWN=$(jq -r '.permissions | keys[]' "$MANIFEST" 2>/dev/null | grep -v -E '^(network|filesystem|subprocess)$' || true)
    
    if [[ -n "$UNKNOWN" ]]; then
        echo -e "${YELLOW}⚠${NC} Unknown permission type: $UNKNOWN"
    fi
fi

echo

# Summary
if [[ $ERRORS -gt 0 ]]; then
    echo -e "${RED}Validation failed with $ERRORS error(s)${NC}"
    exit 2
else
    echo -e "${GREEN}Manifest is valid${NC}"
    exit 0
fi
