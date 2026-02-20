#!/usr/bin/env bash
#
# preflight-check.sh - Run all preflight checks before publishing
#
# Usage:
#   ./preflight-check.sh [directory]
#
# Exit codes:
#   0 - All checks passed
#   1 - Missing requirements
#   2 - Validation failed
#

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

SKILL_DIR="${1:-.}"
ERRORS=0
WARNINGS=0

echo -e "${BLUE}══════════════════════════════════════════════${NC}"
echo -e "${BLUE}         Tank Publish Preflight Check          ${NC}"
echo -e "${BLUE}══════════════════════════════════════════════${NC}"
echo

# 1. Check Tank CLI
echo -e "${BLUE}[1/6] Checking Tank CLI...${NC}"
if command -v tank &> /dev/null; then
    VERSION=$(tank --version 2>/dev/null || echo "unknown")
    echo -e "   ${GREEN}✓${NC} Tank CLI installed: $VERSION"
else
    echo -e "   ${RED}✗${NC} Tank CLI not found"
    echo "      Install: npm install -g @tankpkg/cli"
    ERRORS=$((ERRORS + 1))
fi

# 2. Check authentication
echo -e "${BLUE}[2/6] Checking authentication...${NC}"
if tank whoami &> /dev/null; then
    USER=$(tank whoami 2>/dev/null | head -1 || echo "unknown")
    echo -e "   ${GREEN}✓${NC} Authenticated as: $USER"
else
    echo -e "   ${RED}✗${NC} Not authenticated"
    echo "      Run: tank login"
    ERRORS=$((ERRORS + 1))
fi

# 3. Check required files
echo -e "${BLUE}[3/6] Checking required files...${NC}"

MANIFEST="$SKILL_DIR/skills.json"
if [[ -f "$MANIFEST" ]]; then
    echo -e "   ${GREEN}✓${NC} skills.json found"
else
    echo -e "   ${RED}✗${NC} skills.json not found"
    echo "      Run: tank init"
    ERRORS=$((ERRORS + 1))
fi

SKILL_MD="$SKILL_DIR/SKILL.md"
if [[ -f "$SKILL_MD" ]]; then
    echo -e "   ${GREEN}✓${NC} SKILL.md found"
else
    echo -e "   ${RED}✗${NC} SKILL.md not found"
    echo "      Create a SKILL.md with frontmatter"
    ERRORS=$((ERRORS + 1))
fi

# 4. Validate manifest
echo -e "${BLUE}[4/6] Validating manifest...${NC}"
if [[ -f "$MANIFEST" ]]; then
    if jq empty "$MANIFEST" 2>/dev/null; then
        echo -e "   ${GREEN}✓${NC} Valid JSON syntax"
        
        # Check required fields
        NAME=$(jq -r '.name // empty' "$MANIFEST")
        VERSION=$(jq -r '.version // empty' "$MANIFEST")
        
        if [[ -n "$NAME" ]]; then
            if [[ ${#NAME} -gt 214 ]]; then
                echo -e "   ${RED}✗${NC} Name exceeds 214 characters"
                ERRORS=$((ERRORS + 1))
            elif [[ ! "$NAME" =~ ^(@[a-z0-9-]+/)?[a-z0-9][a-z0-9-]*$ ]]; then
                echo -e "   ${RED}✗${NC} Invalid name format: $NAME"
                ERRORS=$((ERRORS + 1))
            else
                echo -e "   ${GREEN}✓${NC} name: $NAME"
            fi
        else
            echo -e "   ${RED}✗${NC} Missing required field: name"
            ERRORS=$((ERRORS + 1))
        fi
        
        if [[ -n "$VERSION" ]]; then
            if [[ "$VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+ ]]; then
                echo -e "   ${GREEN}✓${NC} version: $VERSION"
            else
                echo -e "   ${RED}✗${NC} Invalid semver: $VERSION"
                ERRORS=$((ERRORS + 1))
            fi
        else
            echo -e "   ${RED}✗${NC} Missing required field: version"
            ERRORS=$((ERRORS + 1))
        fi
    else
        echo -e "   ${RED}✗${NC} Invalid JSON syntax"
        ERRORS=$((ERRORS + 1))
    fi
fi

# 5. Check package size
echo -e "${BLUE}[5/6] Checking package size...${NC}"
if command -v tank &> /dev/null && [[ -f "$MANIFEST" ]]; then
    # Count files (excluding ignored)
    FILE_COUNT=$(find "$SKILL_DIR" -type f \
        ! -path "*/node_modules/*" \
        ! -path "*/.git/*" \
        ! -name "*.log" \
        ! -name ".DS_Store" \
        2>/dev/null | wc -l | tr -d ' ')
    
    if [[ $FILE_COUNT -gt 1000 ]]; then
        echo -e "   ${RED}✗${NC} File count ($FILE_COUNT) exceeds 1000 limit"
        ERRORS=$((ERRORS + 1))
    else
        echo -e "   ${GREEN}✓${NC} File count: $FILE_COUNT (max 1000)"
    fi
    
    # Check directory size
    SIZE_KB=$(du -sk "$SKILL_DIR" 2>/dev/null | cut -f1)
    SIZE_MB=$((SIZE_KB / 1024))
    
    if [[ $SIZE_MB -gt 50 ]]; then
        echo -e "   ${YELLOW}⚠${NC} Directory size: ${SIZE_MB}MB (compressed must be <50MB)"
        WARNINGS=$((WARNINGS + 1))
    else
        echo -e "   ${GREEN}✓${NC} Directory size: ${SIZE_MB}MB"
    fi
fi

# 6. Git status (warning only)
echo -e "${BLUE}[6/6] Checking git status...${NC}"
if git -C "$SKILL_DIR" rev-parse --git-dir &> /dev/null; then
    if git -C "$SKILL_DIR" diff --quiet && git -C "$SKILL_DIR" diff --cached --quiet; then
        echo -e "   ${GREEN}✓${NC} No uncommitted changes"
    else
        echo -e "   ${YELLOW}⚠${NC} Uncommitted changes detected"
        WARNINGS=$((WARNINGS + 1))
    fi
else
    echo -e "   ${YELLOW}⚠${NC} Not a git repository"
fi

# Summary
echo
echo -e "${BLUE}══════════════════════════════════════════════${NC}"

if [[ $ERRORS -gt 0 ]]; then
    echo -e "${RED}FAILED: $ERRORS error(s), $WARNINGS warning(s)${NC}"
    echo
    echo "Fix the errors above before publishing."
    exit 1
elif [[ $WARNINGS -gt 0 ]]; then
    echo -e "${YELLOW}PASSED with $WARNINGS warning(s)${NC}"
    echo
    echo "Review warnings before publishing."
    exit 0
else
    echo -e "${GREEN}ALL CHECKS PASSED${NC}"
    echo
    echo "Ready to publish:"
    echo "  tank publish --dry-run"
    echo "  tank publish"
    exit 0
fi
