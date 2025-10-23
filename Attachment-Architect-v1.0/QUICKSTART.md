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
venv\Scripts\activate
python test_connection.py
```

### 4. Run Scan
```cmd
python jira_dc_scanner.py
```

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
source venv/bin/activate
python test_connection.py
```

### 4. Run Scan
```bash
python jira_dc_scanner.py
```

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

## ❓ Need Help?

- **Connection fails?** Check your URL and token in `.env`
- **Scan is slow?** Normal for large instances (100K+ issues)
- **Want to resume?** Use `python jira_dc_scanner.py --resume SCAN_ID`

See full [README.md](README.md) for detailed documentation.

---

**That's it! You're ready to analyze your Jira storage! 🎉**
