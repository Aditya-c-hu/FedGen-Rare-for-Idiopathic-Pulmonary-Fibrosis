#!/bin/bash
# Helper script to push this project to GitHub

set -e

echo "=========================================================="
echo "          FedGen-Rare GitHub Setup & Push Helper          "
echo "=========================================================="

if [ ! -d ".git" ]; then
    echo "[1/4] Initializing local Git repository..."
    git init
    git branch -M main
else
    echo "[1/4] Git repository already initialized."
fi

echo "[2/4] Staging files..."
git add .

echo "[3/4] Creating commit..."
read -p "Enter commit message (default: 'feat: FedGen-Rare framework for rare disease diagnosis'): " msg
msg=${msg:-"feat: FedGen-Rare framework for rare disease diagnosis"}
git commit -m "$msg" || echo "Nothing new to commit or already committed."

echo "[4/4] Setting up remote repository..."
current_remote=$(git remote get-url origin 2>/dev/null || true)

if [ -z "$current_remote" ]; then
    read -p "Enter your GitHub repository URL (e.g., https://github.com/username/fedgen-rare.git): " repo_url
    if [ -n "$repo_url" ]; then
        git remote add origin "$repo_url"
        echo "Remote origin set to: $repo_url"
    else
        echo "No remote URL provided. You can add it later using:"
        echo "  git remote add origin <your-repo-url>"
        exit 0
    fi
else
    echo "Remote origin already set to: $current_remote"
fi

echo ""
read -p "Push now to origin main? (y/n): " push_now
if [ "$push_now" = "y" ] || [ "$push_now" = "Y" ]; then
    echo "Pushing to GitHub..."
    git push -u origin main
    echo "Successfully pushed to GitHub!"
else
    echo "You can push later by running: git push -u origin main"
fi
