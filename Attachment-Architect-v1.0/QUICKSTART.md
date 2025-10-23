# ⚡ Quick Start Guide

**Get started in 5 minutes using our easy launcher scripts!**

---

## 🪟 Windows Users - Super Easy!

### **Just 4 Simple Steps:**

#### 1️⃣ **Run Setup** (One-time only)
Double-click `setup.bat` or run in Command Prompt:
```cmd
setup.bat
```
✅ Creates virtual environment  
✅ Installs all dependencies  
✅ Creates `.env` file  
✅ Sets up folders  

#### 2️⃣ **Edit Credentials**
Open `.env` in Notepad and add your Jira details:
```
JIRA_BASE_URL=https://your-jira.com
JIRA_TOKEN=your_token_here
```

#### 3️⃣ **Test Connection**
Double-click `test_connection.bat` or run:
```cmd
test_connection.bat
```
✅ Verifies your credentials  
✅ Tests Jira connection  
✅ Shows your user info  

#### 4️⃣ **Run Scan**
Double-click `run_scan.bat` or run:
```cmd
run_scan.bat
```
✅ Scans all attachments  
✅ Generates HTML report  
✅ Shows summary  

#### 5️⃣ **View Report**
The HTML report will be saved in `reports\` folder. Just double-click to open it in your browser!

---

### **✨ Why Use BAT Scripts?**

- 🚀 **No Python knowledge needed** - Just double-click!
- ✅ **Automatic virtual environment** - No manual activation required
- 🔍 **Error checking** - Scripts validate everything before running
- 💬 **Clear messages** - See exactly what's happening
- 🔄 **Resume support** - Easy to continue interrupted scans

---

### **Advanced: Resume Interrupted Scan**

If your scan was interrupted, just run:
```cmd
run_scan.bat --resume SCAN_ID
```

Example:
```cmd
run_scan.bat --resume 9f7629d1
```

---

## Linux/Mac Users

### 1. Run Setup
```bash
chmod +x setup.sh
./setup.sh
```

### 2. Edit Credentials
```bash
nano .env
```
Add your Jira details:
```
JIRA_BASE_URL=https://your-jira.com
JIRA_TOKEN=your_token_here
```

### 3. Test Connection
```bash
chmod +x test_connection.sh
./test_connection.sh
```

### 4. Run Scan
```bash
chmod +x run_scan.sh
./run_scan.sh
```

**Note**: The `.sh` scripts automatically activate the virtual environment for you!

### 5. Open Report
The HTML report will be saved in `reports/` folder. Open it in your browser!

---

## 🔑 Getting a Jira Personal Access Token

1. Log into Jira
2. Click your profile icon → **Personal Access Tokens**
3. Click **Create token**
4. Name: `Attachment Architect`
5. Expiry: Choose duration (or never)
6. Click **Create**
7. **Copy the token** (you won't see it again!)
8. Paste into `.env` file

---

## 🔄 Advanced Commands

### Resume Interrupted Scan
```bash
# Windows
run_scan.bat --resume SCAN_ID

# Linux/Mac
./run_scan.sh --resume SCAN_ID
```

### List All Scans
```bash
python jira_dc_scanner.py --list
```

### Reset and Start Fresh
```bash
python jira_dc_scanner.py --reset
```

### Cleanup Old Scans
```bash
python jira_dc_scanner.py --cleanup 30
```

---

## ❓ Need Help?

- **Connection fails?** Check your URL and token in `.env`
- **Scan is slow?** Normal for large instances (100K+ issues)
- **Want to resume?** Scanner auto-detects incomplete scans
- **Need to reset?** Use `python jira_dc_scanner.py --reset`

See full [README.md](README.md) for detailed documentation.

---

**That's it! You're ready to analyze your Jira storage! 🎉**
