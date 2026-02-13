# 📥 How to Download the breast-ASP Repository

This guide provides **step-by-step instructions** for downloading the breast-ASP repository to your computer.

---

## ✨ Quick Links

**Repository URL**: `https://github.com/nittinnm22-sudo/breast-ASP`

---

## 🎯 Choose Your Method

### Method 1: Download ZIP (Easiest - No Git Required)
### Method 2: Git Clone (Recommended for Developers)
### Method 3: GitHub Desktop (GUI Application)
### Method 4: GitHub CLI (Advanced Users)

---

## Method 1: Download ZIP File (Easiest) ⭐

**Best for**: Beginners, quick access, no Git installation needed

### Steps:

1. **Go to the Repository**
   - Open your web browser
   - Visit: `https://github.com/nittinnm22-sudo/breast-ASP`

2. **Download the ZIP**
   - Click the green **"Code"** button (near the top right)
   - Click **"Download ZIP"**
   - Save the file to your computer (e.g., `Downloads/breast-ASP-main.zip`)

3. **Extract the ZIP**
   - **Windows**: Right-click the ZIP file → "Extract All..." → Choose location
   - **Mac**: Double-click the ZIP file (it extracts automatically)
   - **Linux**: Right-click → "Extract Here" or use command:
     ```bash
     unzip breast-ASP-main.zip
     ```

4. **Open the Folder**
   - Navigate to the extracted folder
   - You should see files like `README.md`, `setup.py`, `src/`, etc.

✅ **Done!** You now have the repository on your computer.

---

## Method 2: Git Clone (Recommended) 🔧

**Best for**: Developers, getting updates, contributing changes

### Prerequisites:
- Git must be installed on your computer
- Check by running: `git --version`
- If not installed, download from: https://git-scm.com/downloads

### Steps:

1. **Open Terminal/Command Prompt**
   - **Windows**: Press `Win + R`, type `cmd`, press Enter
   - **Mac**: Press `Cmd + Space`, type "Terminal", press Enter
   - **Linux**: Press `Ctrl + Alt + T`

2. **Navigate to Your Desired Location**
   ```bash
   cd C:\Users\YourName\Documents  # Windows
   cd ~/Documents                  # Mac/Linux
   ```

3. **Clone the Repository**
   ```bash
   git clone https://github.com/nittinnm22-sudo/breast-ASP.git
   ```

4. **Enter the Directory**
   ```bash
   cd breast-ASP
   ```

5. **Verify the Download**
   ```bash
   ls          # Mac/Linux
   dir         # Windows
   ```

✅ **Done!** You have the repository with full Git history.

### Bonus: Update Your Clone Later
```bash
cd breast-ASP
git pull origin main
```

---

## Method 3: GitHub Desktop (GUI Application) 🖱️

**Best for**: Users who prefer visual interfaces

### Prerequisites:
- Download and install GitHub Desktop: https://desktop.github.com/

### Steps:

1. **Open GitHub Desktop**

2. **Clone a Repository**
   - Click **"File"** → **"Clone Repository"**
   - Or click the **"Clone a repository"** button

3. **Enter Repository URL**
   - Click the **"URL"** tab
   - Paste: `https://github.com/nittinnm22-sudo/breast-ASP`
   - Choose a local path (where to save)
   - Click **"Clone"**

4. **Wait for Download**
   - GitHub Desktop will download all files
   - You'll see a success message when done

5. **Open in File Explorer**
   - Click **"Repository"** → **"Show in Explorer"** (Windows)
   - Or **"Repository"** → **"Show in Finder"** (Mac)

✅ **Done!** You can now easily sync updates with one click.

---

## Method 4: GitHub CLI (Advanced) 💻

**Best for**: Power users, automation, scripting

### Prerequisites:
- Install GitHub CLI: https://cli.github.com/

### Steps:

```bash
# Clone the repository
gh repo clone nittinnm22-sudo/breast-ASP

# Navigate to the folder
cd breast-ASP
```

✅ **Done!** You have the repository via GitHub CLI.

---

## 📁 What You'll Get

After downloading, your folder structure will look like:

```
breast-ASP/
├── README.md                      # Main documentation
├── START_HERE.md                  # Quick start guide
├── setup.py                       # Installation setup
├── requirements.txt               # Python dependencies
├── lung_asp_cli.py               # Lung tumor CLI
├── build_full.sh                 # Build script (Linux/Mac)
├── build_full.bat                # Build script (Windows)
├── src/
│   ├── breast_asp/               # Breast tumor modules
│   │   ├── segmentation.py
│   │   ├── radiomics.py
│   │   └── ...
│   └── lung_asp/                 # Lung tumor modules
│       ├── lung_segmentation.py
│       ├── lung_radiomics.py
│       └── ...
├── examples/
│   ├── example_usage.py          # Breast tumor examples
│   └── lung_examples/
│       └── example_lung_usage.py # Lung tumor examples
├── tests/
│   ├── test_basic.py             # Breast tests
│   └── test_lung.py              # Lung tests
└── docs/
    └── [various documentation files]
```

---

## 🚀 What to Do Next

After downloading the repository:

### 1. Read the Documentation
Start with: **`START_HERE.md`** or **`README.md`**

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Build the Executable (Optional)
```bash
# Linux/Mac
./build_full.sh

# Windows
build_full.bat
```

### 4. Run Examples
```bash
# Breast tumor example
python examples/example_usage.py

# Lung tumor example
python examples/lung_examples/example_lung_usage.py
```

---

## ❓ Troubleshooting

### Issue: "git: command not found"
**Solution**: Git is not installed. Download from https://git-scm.com/downloads

### Issue: "Permission denied" when cloning
**Solution**: The repository might be private. Make sure you have access.

### Issue: "Connection timeout"
**Solution**: 
- Check your internet connection
- Try downloading the ZIP file instead
- If behind a firewall, ask your IT department

### Issue: ZIP file won't extract
**Solution**:
- Make sure you have enough disk space
- Try using a different extraction tool (7-Zip, WinRAR, etc.)
- Re-download the ZIP file (it might be corrupted)

### Issue: Can't find the downloaded files
**Solution**:
- Check your Downloads folder
- Search your computer for "breast-ASP"
- For Git clone, check the directory you were in when you ran the command

---

## 💡 Pro Tips

### Keep Your Copy Updated (Git Clone Only)
```bash
cd breast-ASP
git pull
```

### Download a Specific Version
```bash
# Clone a specific branch
git clone -b branch-name https://github.com/nittinnm22-sudo/breast-ASP.git

# Or download a specific release ZIP from:
# https://github.com/nittinnm22-sudo/breast-ASP/releases
```

### Download Only What You Need
If you just want to test, download the ZIP. If you want to contribute or stay updated, use Git clone.

---

## 📞 Need More Help?

- **Documentation**: Check `START_HERE.md` for build instructions
- **GitHub Issues**: https://github.com/nittinnm22-sudo/breast-ASP/issues
- **General Git Help**: https://git-scm.com/doc

---

## 📝 Quick Command Reference

```bash
# Download via Git
git clone https://github.com/nittinnm22-sudo/breast-ASP.git
cd breast-ASP

# Update your local copy
git pull

# Check what branch you're on
git branch

# Switch to a different branch
git checkout branch-name
```

---

## ✅ Verification

After downloading, verify you have the correct files:

```bash
# Should show the main files
ls -la

# Should show Python files in src directory
ls src/

# Test import (after installing dependencies)
python -c "from src.lung_asp import lung_segmentation; print('Success!')"
```

---

**That's it! You now know all the ways to download the breast-ASP repository.** 🎉

Choose the method that works best for you and get started!
