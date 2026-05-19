# Investment Dashboard - Cross-User Setup Guide

## Repository Information
- **GitHub URL**: git@github.com:mohdmotasim/investment-dashboard.git
- **Local Path**: C:\Users\HP\OneDrive\Desktop\Bis (or C:\Users\Motasim\CascadeProjects\Bis)
- **Git Remote**: origin

## Setup Instructions for Both Laptop Users

### For User HP (LAPTOP-VU0LE4G4\HP)

#### First Time Setup (if not already done)
```bash
# Navigate to project directory
cd "C:\Users\HP\OneDrive\Desktop\Bis"

# Configure git user (if not configured)
git config --global user.name "HP"
git config --global user.email "your-email@example.com"

# Add safe directory (fixes ownership issues)
git config --global --add safe.directory C:/Users/HP/OneDrive/Desktop/Bis

# Verify remote is configured
git remote -v
# Should show: origin git@github.com:mohdmotasim/investment-dashboard.git
```

#### Daily Workflow
```bash
# Navigate to project
cd "C:\Users\HP\OneDrive\Desktop\Bis"

# Pull latest changes before starting work
git pull origin main

# Make your changes to app.py or other files

# Stage and commit changes
git add .
git commit -m "Your descriptive commit message"

# Push changes to GitHub
git push origin main
```

### For User Motasim (LAPTOP-VU0LE4G4\Motasim)

#### First Time Setup
```bash
# Navigate to your preferred project directory
cd "C:\Users\Motasim\CascadeProjects"

# Clone the repository
git clone git@github.com:mohdmotasim/investment-dashboard.git Bis

# Navigate into the cloned directory
cd Bis

# Configure git user (if not configured)
git config --global user.name "MotasimAleem"
git config --global user.email "mohdmotasim.a@somaiya.edu"

# Add safe directory (fixes ownership issues)
git config --global --add safe.directory C:/Users/Motasim/CascadeProjects/Bis

# Verify setup
git remote -v
git status
```

#### Daily Workflow
```bash
# Navigate to project
cd "C:\Users\Motasim\CascadeProjects\Bis"

# Pull latest changes before starting work
git pull origin main

# Make your changes to app.py or other files

# Stage and commit changes
git add .
git commit -m "Your descriptive commit message"

# Push changes to GitHub
git push origin main
```

## Common Issues & Solutions

### Issue: "fatal: detected dubious ownership in repository"
**Solution**: Add the directory to git's safe directories:
```bash
git config --global --add safe.directory <full-path-to-repository>
```

### Issue: "Permission denied (publickey)" when pushing
**Solution**: Set up SSH keys for GitHub:
1. Generate SSH key: `ssh-keygen -t ed25519 -C "your-email@example.com"`
2. Add to GitHub: Settings → SSH and GPG keys → New SSH key
3. Test connection: `ssh -T git@github.com`

### Issue: Merge conflicts when pulling
**Solution**:
```bash
git pull origin main
# If conflicts occur, resolve them in the conflicted files
git add <resolved-files>
git commit -m "Resolve merge conflicts"
git push origin main
```

## Project Structure
```
Bis/
├── app.py                      # Main Streamlit application
├── portfolio.csv               # Sample holdings export
├── voice_to_chat.py            # Standalone voice-to-text helper
├── CLOUD_CONTEXT.md            # Project documentation
├── SETUP_GUIDE.md              # This file
├── conviction_board/           # Custom component assets (dormant)
├── .git-hooks/                 # Git automation scripts
└── .vscode/                    # VS Code configuration
```

## Running the Application

```bash
# Activate virtual environment (if using one)
# Windows PowerShell:
.venv\Scripts\Activate.ps1

# Install dependencies (if not already installed)
pip install streamlit yfinance pandas plotly feedparser

# Run the dashboard
streamlit run app.py
```

## Git Best Practices

1. **Always pull before pushing**: `git pull origin main` before making changes
2. **Write descriptive commit messages**: Explain what and why, not just what
3. **Commit frequently**: Small, focused commits are easier to review and revert
4. **Don't commit sensitive data**: Never commit API keys, passwords, or personal data
5. **Review changes before committing**: Use `git diff` to review your changes

## Syncing Between Users

When switching between laptops:
1. Always `git pull origin main` to get the latest changes
2. Resolve any merge conflicts if both users edited the same files
3. Test the application after pulling changes
4. Push your changes when done

## Contact & Support

- **GitHub Repository**: https://github.com/mohdmotasim/investment-dashboard
- **Project Documentation**: See CLOUD_CONTEXT.md for detailed project information
