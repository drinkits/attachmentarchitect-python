# 🚀 Launcher Scripts Guide

**Easy-to-use BAT and SH scripts for hassle-free operation**

---

## 🎯 Overview

Attachment Architect includes **launcher scripts** that make it incredibly easy to use - no Python knowledge required!

### **Available Scripts**

#### **Setup Scripts** (One-time)
- `setup.bat` (Windows)
- `setup.sh` (Linux/Mac)

#### **Launcher Scripts** (Daily use)
- `run_scan.bat` / `run_scan.sh` - Run the scanner
- `test_connection.bat` / `test_connection.sh` - Test Jira connection

---

## 🪟 Windows Users

### **Super Easy - Just Double-Click!**

1. **Double-click `setup.bat`** → Sets up everything
2. **Edit `.env` in Notepad** → Add your credentials
3. **Double-click `test_connection.bat`** → Verify connection
4. **Double-click `run_scan.bat`** → Run the scan!

### **Or Use Command Prompt:**

```cmd
setup.bat
# Edit .env
test_connection.bat
run_scan.bat
```

---

## 🐧 Linux/Mac Users

### **Simple Terminal Commands:**

```bash
# One-time setup
chmod +x *.sh
./setup.sh

# Edit credentials
nano .env

# Test connection
./test_connection.sh

# Run scan
./run_scan.sh
```

---

## ✨ Why Use Launcher Scripts?

### **1. No Manual Virtual Environment Activation** ✅
The scripts automatically:
- Detect if virtual environment exists
- Activate it before running
- Show clear error if not set up

**Without scripts:**
```cmd
# Windows - Manual way
venv\Scripts\activate
python jira_dc_scanner.py
```

**With scripts:**
```cmd
# Windows - Easy way
run_scan.bat
```

### **2. Built-in Error Checking** ✅
Scripts validate:
- ✅ Virtual environment exists
- ✅ `.env` file exists
- ✅ Python is installed
- ✅ Dependencies are installed

### **3. Clear User Messages** ✅
```
========================================
Attachment Architect - Scanner
========================================

[✓] Virtual environment found
[✓] Configuration file found
[✓] Starting scan...
```

### **4. Resume Support** ✅
```cmd
# Easy resume
run_scan.bat --resume 9f7629d1

# vs manual
venv\Scripts\activate
python jira_dc_scanner.py --resume 9f7629d1
```

---

## 📋 Script Details

### **setup.bat / setup.sh**

**What it does:**
1. Checks Python installation
2. Creates virtual environment
3. Installs dependencies from `requirements.txt`
4. Creates `.env` from `.env.example`
5. Creates necessary folders (`reports/`, `scans/`, `logs/`)

**When to use:**
- First time setup
- After updating dependencies
- If virtual environment gets corrupted

**Example output:**
```
========================================
Attachment Architect - Setup
========================================

[1/5] Checking Python...
Python 3.10.0 found

[2/5] Creating virtual environment...
Virtual environment created successfully

[3/5] Installing dependencies...
Dependencies installed successfully

[4/5] Setting up configuration...
.env file created from template
IMPORTANT: Edit .env file with your Jira credentials!

[5/5] Creating directories...
Directories created

========================================
Setup Complete!
========================================
```

---

### **test_connection.bat / test_connection.sh**

**What it does:**
1. Activates virtual environment
2. Runs `test_connection.py`
3. Shows connection status

**When to use:**
- After initial setup
- After changing credentials
- To verify Jira is accessible
- Troubleshooting connection issues

**Example output:**
```
========================================
Attachment Architect - Connection Test
========================================

[✓] Virtual environment found
[✓] Configuration file found
[✓] Testing connection...

✓ Connected to Jira successfully!
✓ User: John Doe (john.doe)
✓ Authentication working

========================================
Connection Test Complete!
========================================
```

---

### **run_scan.bat / run_scan.sh**

**What it does:**
1. Activates virtual environment
2. Runs `jira_dc_scanner.py`
3. Passes any command-line arguments

**When to use:**
- To run a new scan
- To resume an interrupted scan
- Daily/weekly scanning

**Basic usage:**
```cmd
run_scan.bat
```

**Resume usage:**
```cmd
run_scan.bat --resume 9f7629d1
```

**Example output:**
```
========================================
Attachment Architect - Scanner
========================================

[✓] Virtual environment found
[✓] Configuration file found
[✓] Starting scan...

Loading configuration...
Connecting to Jira...
✓ Connected successfully

Starting new scan...

Analyzing Issues: 100%|████████| 10000/10000 [15:30<00:00]

========================================
SCAN SUMMARY
========================================
Scan ID: 9f7629d1
Duration: 930.5 seconds
Issues Processed: 10,000

Total Files: 7,063
Total Storage: 7.00 GB
...
```

---

## 🔧 Advanced Usage

### **Resume Interrupted Scans**

**Windows:**
```cmd
run_scan.bat --resume SCAN_ID
```

**Linux/Mac:**
```bash
./run_scan.sh --resume SCAN_ID
```

### **Custom Python Commands**

The launcher scripts support passing arguments:

```cmd
# Windows
run_scan.bat --list
run_scan.bat --reset
run_scan.bat --cleanup 30

# Linux/Mac
./run_scan.sh --list
./run_scan.sh --reset
./run_scan.sh --cleanup 30
```

---

## 🛠️ Troubleshooting

### **"Virtual environment not found"**

**Problem:** Scripts can't find `venv/` folder

**Solution:**
```cmd
# Run setup again
setup.bat  # Windows
./setup.sh  # Linux/Mac
```

---

### **".env file not found"**

**Problem:** Configuration file missing

**Solution:**
```cmd
# Copy example file
copy .env.example .env  # Windows
cp .env.example .env    # Linux/Mac

# Then edit with your credentials
```

---

### **"Python not found"**

**Problem:** Python not installed or not in PATH

**Solution:**
- **Windows:** Install from [python.org](https://python.org)
- **Linux:** `sudo apt install python3 python3-venv`
- **Mac:** `brew install python3`

---

### **Scripts won't run (Linux/Mac)**

**Problem:** Scripts not executable

**Solution:**
```bash
chmod +x *.sh
```

---

## 📊 Comparison: Manual vs Scripts

### **Manual Method** ❌
```cmd
# Windows
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
# Edit .env
mkdir reports scans logs
python test_connection.py
python jira_dc_scanner.py
```

### **Script Method** ✅
```cmd
# Windows
setup.bat
# Edit .env
test_connection.bat
run_scan.bat
```

**Time saved:** ~5 minutes per use  
**Errors avoided:** Many!  
**Ease of use:** Much better!

---

## 🎯 Best Practices

### **For First-Time Users**
1. ✅ Use `setup.bat` / `setup.sh` for initial setup
2. ✅ Always test connection before scanning
3. ✅ Use launcher scripts instead of manual commands
4. ✅ Keep scripts in the same folder as the application

### **For Regular Users**
1. ✅ Use `run_scan.bat` / `run_scan.sh` for daily scans
2. ✅ Use `--resume` flag if scan is interrupted
3. ✅ Check logs if something goes wrong
4. ✅ Re-run `setup.bat` if dependencies change

### **For Advanced Users**
1. ✅ Scripts support all command-line arguments
2. ✅ Can be scheduled with Task Scheduler (Windows) or cron (Linux)
3. ✅ Can be called from other scripts
4. ✅ Exit codes indicate success/failure

---

## 🚀 Quick Reference

### **Windows**
```cmd
setup.bat                    # One-time setup
test_connection.bat          # Test connection
run_scan.bat                 # Run scan
run_scan.bat --resume ID     # Resume scan
```

### **Linux/Mac**
```bash
./setup.sh                   # One-time setup
./test_connection.sh         # Test connection
./run_scan.sh                # Run scan
./run_scan.sh --resume ID    # Resume scan
```

---

## 💡 Pro Tips

### **Tip 1: Create Desktop Shortcuts (Windows)**
Right-click `run_scan.bat` → Send to → Desktop (create shortcut)

### **Tip 2: Schedule Regular Scans**
**Windows Task Scheduler:**
```
Program: C:\path\to\run_scan.bat
Start in: C:\path\to\Attachment-Architect-v1.0
```

**Linux/Mac cron:**
```bash
0 2 * * 0 cd /path/to/Attachment-Architect-v1.0 && ./run_scan.sh
```

### **Tip 3: Batch Processing**
Create a custom batch file:
```cmd
@echo off
call test_connection.bat
if %ERRORLEVEL% EQU 0 (
    call run_scan.bat
)
```

---

## 📚 Related Documentation

- **README.md** - Full documentation
- **QUICKSTART.md** - 5-minute guide
- **INSTALLATION_GUIDE.md** - Detailed setup
- **TROUBLESHOOTING.md** - Common issues

---

## ✅ Summary

**Launcher scripts make Attachment Architect:**
- ✅ Easy to use (no Python knowledge needed)
- ✅ Error-proof (built-in validation)
- ✅ Professional (clear messages)
- ✅ Efficient (saves time)
- ✅ Reliable (consistent behavior)

**Just double-click and go!** 🚀

---

**Attachment Architect v1.0**  
**Made with ❤️ by Attachment Architect Team**
