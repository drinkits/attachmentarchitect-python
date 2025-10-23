# ⚡ Quick Start Guide

**Get started in 5 minutes!**

---

## Windows Users

### 1. Run Setup
```cmd
setup.bat
```

### 2. Edit Credentials
Open `.env` in Notepad and add your Jira details:
```
JIRA_BASE_URL=https://your-jira.com
JIRA_TOKEN=your_token_here
```

### 3. Test Connection
```cmd
test_connection.bat
```

### 4. Run Scan
```cmd
run_scan.bat
```

**Note**: The `.bat` scripts automatically activate the virtual environment for you!

### 5. Open Report
The HTML report will be saved in `reports\` folder. Open it in your browser!

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
