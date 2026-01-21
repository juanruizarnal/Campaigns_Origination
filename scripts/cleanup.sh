#!/bin/bash
# =============================================================================
# Cleanup Script - Remove unnecessary files from repository
# =============================================================================
# This script removes documentation and template folders that are not needed
# for production deployment.
#
# Usage:
#   ./scripts/cleanup.sh          # Dry run (show what would be deleted)
#   ./scripts/cleanup.sh --force  # Actually delete files
# =============================================================================

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Change to project root
cd "$(dirname "$0")/.."

echo ""
echo "=========================================="
echo "Alter-5 Repository Cleanup Script"
echo "=========================================="
echo ""

# Directories to remove
DIRS_TO_REMOVE=(
    "A.Templates"
    "B.Project_Context"
    "C.Deliverables"
    "Claude-Projects"
    "test_apis"
    "docs"
)

# Files to remove
FILES_TO_REMOVE=(
    ".DS_Store"
    "**/.DS_Store"
    "*.pyc"
    "**/__pycache__"
)

# Calculate size
calculate_size() {
    local total=0
    for dir in "${DIRS_TO_REMOVE[@]}"; do
        if [ -d "$dir" ]; then
            size=$(du -sk "$dir" 2>/dev/null | cut -f1)
            total=$((total + size))
        fi
    done
    echo $total
}

# Show what will be deleted
echo -e "${YELLOW}The following directories will be removed:${NC}"
echo ""

for dir in "${DIRS_TO_REMOVE[@]}"; do
    if [ -d "$dir" ]; then
        size=$(du -sh "$dir" 2>/dev/null | cut -f1)
        count=$(find "$dir" -type f 2>/dev/null | wc -l | tr -d ' ')
        echo -e "  ${RED}✗${NC} $dir/ (${size}, ${count} files)"
    else
        echo -e "  ${GREEN}✓${NC} $dir/ (already removed)"
    fi
done

echo ""
total_size=$(calculate_size)
echo -e "Total size to free: ${YELLOW}${total_size}K${NC}"
echo ""

# Check for --force flag
if [ "$1" == "--force" ]; then
    echo -e "${RED}Deleting files...${NC}"
    echo ""

    for dir in "${DIRS_TO_REMOVE[@]}"; do
        if [ -d "$dir" ]; then
            rm -rf "$dir"
            echo -e "  ${GREEN}✓${NC} Removed $dir/"
        fi
    done

    # Remove .DS_Store files
    find . -name ".DS_Store" -delete 2>/dev/null || true
    echo -e "  ${GREEN}✓${NC} Removed .DS_Store files"

    # Remove __pycache__ directories
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    echo -e "  ${GREEN}✓${NC} Removed __pycache__ directories"

    # Remove .pyc files
    find . -name "*.pyc" -delete 2>/dev/null || true
    echo -e "  ${GREEN}✓${NC} Removed .pyc files"

    echo ""
    echo -e "${GREEN}Cleanup complete!${NC}"
    echo ""
    echo "You can now commit the changes:"
    echo "  git add -A"
    echo "  git commit -m 'chore: Remove unnecessary documentation and templates'"

else
    echo -e "${YELLOW}This is a dry run. No files were deleted.${NC}"
    echo ""
    echo "To actually delete files, run:"
    echo -e "  ${GREEN}./scripts/cleanup.sh --force${NC}"
    echo ""
    echo "Note: Make sure you have a backup or the files are committed to git first!"
fi

echo ""
