# Fix: PyInstaller Using Wrong Python Environment

## 🔧 Issue

PyInstaller is running from **Miniconda (Python 3.13.5)** instead of your **virtual environment (Python 3.10.11)**.

**Symptom:**
```
PyInstaller is running from Miniconda (Python 3.13.5) 
even though you activated your .venv (Python 3.10.11)
```

**Problem**: This causes build failures because:
- Python 3.13 may not be compatible with all dependencies
- PyInstaller in Miniconda may not find packages in your venv
- Mixed environments cause conflicts

---

## ✅ Quick Solution

### Step 1: Verify Your Environment

**Check where Python is coming from:**
```cmd
where python
```

**Expected (good):**
```
C:\Users\nitin\Desktop\Lung_ASP\lung_env\Scripts\python.exe
C:\Users\nitin\miniconda3\python.exe
```

**Bad (if venv not first):**
```
C:\Users\nitin\miniconda3\python.exe
C:\Users\nitin\Desktop\Lung_ASP\lung_env\Scripts\python.exe
```

### Step 2: Use Updated Build Script

The fixed `build_full.bat` now explicitly uses your virtual environment!

**Download the updated script:**
```cmd
cd C:\Users\nitin\Desktop\Lung_ASP
git pull origin main
```

**Or manually update** (see instructions below)

---

## 🔄 Option 1: Use Updated Build Script (Recommended)

The updated `build_full.bat` automatically:
1. Detects if you're in a virtual environment
2. Uses the correct Python/pip/pyinstaller from that environment
3. Warns you if no virtual environment is active

**Just run:**
```cmd
cd C:\Users\nitin\Desktop\Lung_ASP
lung_env\Scripts\activate
build_full.bat
```

**Expected output:**
```
Step 1: Checking Python version and virtual environment...
✓ Virtual environment detected: C:\Users\nitin\Desktop\Lung_ASP\lung_env
Using Python from: C:\Users\nitin\Desktop\Lung_ASP\lung_env\Scripts\python.exe
Python 3.10.11
```

Perfect! ✅

---

## 🔄 Option 2: Use Explicit Paths (Manual)

If you can't update the script, use explicit paths:

### Method A: Activate Virtual Environment FIRST

**Make sure to activate:**
```cmd
cd C:\Users\nitin\Desktop\Lung_ASP
lung_env\Scripts\activate.bat
```

**Verify it's active:**
```cmd
where python
python --version
```

Should show your venv Python (3.10.11), not Miniconda (3.13.5).

### Method B: Use Full Paths in Commands

**Instead of:**
```cmd
pip install -e .
pyinstaller lung_asp.spec
```

**Use:**
```cmd
lung_env\Scripts\pip.exe install -e .
lung_env\Scripts\pyinstaller.exe lung_asp.spec
```

This forces use of the venv tools.

---

## 🔍 Why This Happens

### Common Causes:

1. **PATH Order**
   - Miniconda is earlier in PATH than venv
   - Windows finds Miniconda's python.exe first

2. **Virtual Environment Not Activated**
   - Forgot to run `activate`
   - Activation failed silently

3. **Conflicting Python Installations**
   - System Python
   - Miniconda
   - Virtual environment
   - All competing

4. **PowerShell vs CMD**
   - Different activation commands
   - Different environment variables

---

## ✅ Permanent Fix

### Option A: Fix PATH Order

**Add your venv to PATH first:**

1. Open System Properties → Environment Variables
2. Edit "Path" in User variables
3. Move or add: `C:\Users\nitin\Desktop\Lung_ASP\lung_env\Scripts`
4. Move it to the TOP of the list
5. Click OK, restart CMD

**Verify:**
```cmd
where python
```

Should show venv first.

### Option B: Use Virtual Environment Exclusively

**Always activate before building:**

Create a batch file `build_in_venv.bat`:
```batch
@echo off
call lung_env\Scripts\activate.bat
build_full.bat
```

Run this instead of build_full.bat directly.

### Option C: Remove Miniconda from PATH (Nuclear Option)

If you don't need Miniconda system-wide:

1. Open Environment Variables
2. Edit "Path"
3. Remove Miniconda entries
4. Click OK, restart CMD

**Warning**: This affects all applications!

---

## 🛠️ Troubleshooting

### Issue 1: Virtual Environment Won't Activate

**Symptom:**
```cmd
lung_env\Scripts\activate
'activate' is not recognized as an internal or external command
```

**Solution:**
```cmd
REM Create venv if it doesn't exist
python -m venv lung_env

REM Use .bat extension
lung_env\Scripts\activate.bat
```

### Issue 2: Activation Seems to Work But Still Uses Wrong Python

**Check:**
```cmd
echo %VIRTUAL_ENV%
```

**If empty**, activation failed. Try:
```cmd
REM Full path
C:\Users\nitin\Desktop\Lung_ASP\lung_env\Scripts\activate.bat

REM Check again
echo %VIRTUAL_ENV%
where python
```

### Issue 3: PyInstaller Not in Virtual Environment

**Install in venv:**
```cmd
lung_env\Scripts\activate
pip install pyinstaller>=5.10.0
```

**Verify:**
```cmd
where pyinstaller
```

Should show: `C:\Users\nitin\Desktop\Lung_ASP\lung_env\Scripts\pyinstaller.exe`

### Issue 4: Multiple Python Versions Conflicting

**Solution - Use Python Launcher:**
```cmd
py -3.10 -m venv lung_env
lung_env\Scripts\activate
py -3.10 -m pip install pyinstaller
```

This forces Python 3.10 specifically.

---

## ✅ Verification Checklist

After applying fixes, verify:

- [ ] Virtual environment activates: `lung_env\Scripts\activate`
- [ ] VIRTUAL_ENV is set: `echo %VIRTUAL_ENV%`
- [ ] Python is from venv: `where python` (venv listed first)
- [ ] Python version correct: `python --version` (3.10.11)
- [ ] PyInstaller from venv: `where pyinstaller` (venv path)
- [ ] Can import packages: `python -c "import torch; print('OK')"`
- [ ] Build script detects venv: Run `build_full.bat`, see "✓ Virtual environment detected"

**All checked? You're good to go!** ✅

---

## 🎯 Recommended Workflow

### Every Time You Build:

1. **Open fresh CMD window**
   ```cmd
   cd C:\Users\nitin\Desktop\Lung_ASP
   ```

2. **Activate virtual environment**
   ```cmd
   lung_env\Scripts\activate
   ```

3. **Verify environment**
   ```cmd
   echo %VIRTUAL_ENV%
   python --version
   ```

4. **Run build**
   ```cmd
   build_full.bat
   ```

5. **Done!**

---

## 📋 Quick Reference

| Problem | Quick Fix |
|---------|-----------|
| Wrong Python | Activate venv first |
| Can't activate | Use `activate.bat` |
| Miniconda taking over | Use explicit paths |
| PyInstaller not found | Install in venv |
| PATH issues | Put venv first in PATH |
| Still wrong Python | Use `lung_env\Scripts\python.exe` directly |

---

## 🔗 Related Docs

- `TROUBLESHOOTING_WINDOWS.md` - General Windows issues
- `WINDOWS_BUILD_INSTRUCTIONS.md` - Complete build guide
- `FIX_FOR_BUILD_ERROR.md` - Setup.py errors

---

## ✨ Summary

**Problem**: PyInstaller using Miniconda instead of venv

**Root Cause**: PATH order or venv not activated

**Solution**: 
1. Use updated `build_full.bat` (auto-detects venv)
2. Or: Activate venv before building
3. Or: Use explicit paths to venv Python/PyInstaller

**Verification**: 
```cmd
where python
# Should show: C:\...\lung_env\Scripts\python.exe FIRST
```

**Result**: Build uses correct Python environment! ✅

---

*Updated: 2026-02-13*
