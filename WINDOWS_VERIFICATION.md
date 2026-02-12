# 🪟 Windows Verification Guide

## ✅ How to Verify Repository Contents on Windows

This guide helps Windows users verify that both **breast_asp** and **lung_asp** packages are included after cloning the repository.

---

## 📋 Step-by-Step Verification

### Step 1: Clone the Repository

```cmd
git clone https://github.com/nittinnm22-sudo/breast-ASP.git
```

**Expected Output:**
```
Cloning into 'breast-ASP'...
remote: Enumerating objects: 150, done.
remote: Counting objects: 100% (150/150), done.
remote: Compressing objects: 100% (117/117), done.
remote: Total 150 (delta 58), reused 114 (delta 26), pack-reused 0 (from 0)
Receiving objects: 100% (150/150), 125.47 KiB | 636.00 KiB/s, done.
Resolving deltas: 100% (58/58), done.
```

✅ **Success!** Repository cloned successfully.

---

### Step 2: Navigate into the Directory

```cmd
cd breast-ASP
```

**⚠️ Common Mistake:**
```cmd
cd breast-ASPcd breast-ASP    ❌ WRONG (missing space)
```

**✅ Correct:**
```cmd
cd breast-ASP    ✅ CORRECT
```

---

### Step 3: Verify You're in the Right Directory

```cmd
cd
```

**Expected Output:**
```
C:\Users\YourName\breast-ASP
```

Or use:
```cmd
echo %CD%
```

**Expected Output:**
```
C:\Users\YourName\breast-ASP
```

✅ If you see `breast-ASP` in the path, you're in the right place!

---

### Step 4: List Directory Contents

**Option A: Using `dir` (Windows native)**
```cmd
dir
```

**Expected Output (partial):**
```
 Directory of C:\Users\YourName\breast-ASP

BUILD_CHECKLIST.md
BUILD_EXECUTABLE.md
README.md
setup.py
src
tests
...
```

**Option B: Using PowerShell**
```powershell
ls
```

or

```powershell
Get-ChildItem
```

---

### Step 5: Verify the `src` Directory Exists

**Using `dir`:**
```cmd
dir src
```

**Using PowerShell:**
```powershell
ls src
```

**Expected Output:**
```
 Directory of C:\Users\YourName\breast-ASP\src

breast_asp
lung_asp
```

✅ **Both packages are there!**

---

### Step 6: Check Contents of Each Package

**Check breast_asp:**
```cmd
dir src\breast_asp
```

**Expected Output:**
```
__init__.py
exclusion.py
pipeline.py
radiomics.py
segmentation.py
```

**Check lung_asp:**
```cmd
dir src\lung_asp
```

**Expected Output:**
```
__init__.py
dicom_converter.py
lung_exclusion.py
lung_pipeline.py
lung_radiomics.py
lung_segmentation.py
nnunet_wrapper.py
qc_visualization.py
totalsegmentor_wrapper.py
```

✅ **Both packages are complete!**

---

## 🔍 Quick Verification Command

Run this single command to verify everything:

**Command Prompt:**
```cmd
dir src /b
```

**PowerShell:**
```powershell
ls src | Select-Object Name
```

**Expected Output:**
```
breast_asp
lung_asp
```

✅ **If you see both, you're all set!**

---

## ⚠️ Common Issues and Solutions

### Issue 1: "The system cannot find the path specified"

**Problem:** You're not in the correct directory.

**Solution:**
```cmd
cd C:\Users\YourName\breast-ASP
```

Replace `YourName` with your actual Windows username.

---

### Issue 2: "ls: cannot access 'src/'"

**Problem:** You're using Linux/Git Bash syntax on Windows Command Prompt.

**Solution:**
- **Windows Command Prompt:** Use `dir src` instead of `ls src/`
- **PowerShell:** Use `ls src` or `dir src`
- **Git Bash:** Use `ls src/` (with forward slash)

---

### Issue 3: Can't Find the Repository Folder

**Solution:**
1. Find where you cloned it:
   ```cmd
   cd C:\Users\YourName
   dir /b | findstr breast-ASP
   ```

2. Navigate to it:
   ```cmd
   cd breast-ASP
   ```

---

## 🐍 Verify Python Installation

Before using the packages, verify Python is installed:

```cmd
python --version
```

**Expected Output:**
```
Python 3.8.10 (or higher)
```

If not installed, download from: https://www.python.org/downloads/

---

## 📦 Install the Packages

After verification, install the packages:

```cmd
pip install -e .
```

**Expected Output:**
```
Successfully installed breast-ASP
```

---

## ✅ Verify Installation

Test imports in Python:

```cmd
python -c "import breast_asp; print('breast_asp: OK')"
python -c "import lung_asp; print('lung_asp: OK')"
```

**Expected Output:**
```
breast_asp: OK
lung_asp: OK
```

✅ **Both packages work!**

---

## 🎯 Complete Verification Script

Copy and paste this entire block into Command Prompt:

```cmd
@echo off
echo.
echo ========================================
echo   Breast-ASP Repository Verification
echo ========================================
echo.
echo Current Directory:
cd
echo.
echo Checking src directory...
dir src /b
echo.
echo Checking breast_asp package...
dir src\breast_asp /b | findstr ".py"
echo.
echo Checking lung_asp package...
dir src\lung_asp /b | findstr ".py"
echo.
echo ========================================
echo   Verification Complete!
echo ========================================
echo.
echo Both breast_asp and lung_asp are present!
echo.
```

---

## 📝 Summary

### What You Should See:

```
C:\Users\YourName> git clone https://github.com/nittinnm22-sudo/breast-ASP.git
✅ Clone successful

C:\Users\YourName> cd breast-ASP
✅ Navigated to repository

C:\Users\YourName\breast-ASP> dir src
✅ Found: breast_asp and lung_asp

C:\Users\YourName\breast-ASP> pip install -e .
✅ Installation successful

C:\Users\YourName\breast-ASP> python -c "import breast_asp, lung_asp"
✅ Both packages import correctly
```

---

## 🆘 Still Having Issues?

### Check These:

1. **Are you in the right directory?**
   ```cmd
   cd
   ```
   Should show path ending in `breast-ASP`

2. **Did you clone successfully?**
   ```cmd
   dir /b | findstr README
   ```
   Should show `README.md`

3. **Is Git installed?**
   ```cmd
   git --version
   ```
   Should show Git version

---

## 🎓 Windows Command Reference

| Task | Command Prompt | PowerShell |
|------|---------------|------------|
| List files | `dir` | `ls` or `Get-ChildItem` |
| Change directory | `cd folder` | `cd folder` |
| Current directory | `cd` | `pwd` |
| Find files | `dir /b` | `ls \| Select-Object Name` |
| Environment variable | `echo %VAR%` | `$env:VAR` |

---

## ✅ Success Criteria

You've successfully verified the repository when:

- ✅ Repository cloned without errors
- ✅ You can navigate to `breast-ASP` directory
- ✅ `src` directory exists
- ✅ `src\breast_asp` directory exists with 5 Python files
- ✅ `src\lung_asp` directory exists with 9 Python files
- ✅ Both packages can be imported in Python

**Congratulations! You have both breast-ASP and lung-ASP ready to use!** 🎉

---

## 📚 Next Steps

Now that you've verified the repository:

1. **Read the main guide:** `README.md`
2. **Install dependencies:** `pip install -r requirements.txt`
3. **Try examples:** Check `examples/` directory
4. **Build executable:** See `BUILD_LOCAL.md` for Windows
5. **Learn more:** Read `FAQ.md` for common questions

---

## 🔗 Related Documentation

- [README.md](README.md) - Main documentation
- [FAQ.md](FAQ.md) - Frequently asked questions
- [BUILD_LOCAL.md](BUILD_LOCAL.md) - Building on Windows
- [YES_IT_INCLUDES_LUNG_ASP.md](YES_IT_INCLUDES_LUNG_ASP.md) - Confirmation both packages included

---

**Windows users: You've got everything you need!** 🪟✅
