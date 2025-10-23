# 📦 Installation Guide - Attachment Architect v1.0

**Complete installation instructions for all platforms**

---

## 📋 Pre-Installation Checklist

Before you begin, ensure you have:

- [ ] **Python 3.8 or higher** installed
- [ ] **Network access** to your Jira Data Center instance
- [ ] **Jira credentials** (Personal Access Token or username/password)
- [ ] **Read permissions** for issues and attachments in Jira
- [ ] **100 MB free disk space** (minimum)

---

## 🪟 Windows Installation

### Step 1: Extract Package

Extract the `Attachment-Architect-v1.0` folder to your desired location:
```
C:\Users\YourName\Documents\Attachment-Architect-v1.0\
```

### Step 2: Run Setup

Open Command Prompt or PowerShell in the package folder and run:

```cmd
setup.bat
```

**What it does:**
- ✅ Checks Python installation
- ✅ Creates virtual environment (`venv/`)
- ✅ Installs all dependencies
- ✅ Creates `.env` from template
- ✅ Creates folders: `reports/`, `scans/`, `logs/`

**Expected output:**
```
========================================
Attachment Architect - Setup
========================================

[1/5] Python found
Python 3.10.0

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

### Step 3: Configure Credentials

Edit `.env` file (use Notepad or any text editor):

```env
JIRA_BASE_URL=https://your-jira-instance.com
JIRA_TOKEN=your_personal_access_token_here
```

**Getting a Personal Access Token:**
1. Log into Jira
2. Click profile icon → **Personal Access Tokens**
3. Click **Create token**
4. Name: `Attachment Architect`
5. Click **Create** and copy the token

### Step 4: Test Connection

```cmd
test_connection.bat
```

**Expected output:**
```
✓ Connected to Jira successfully!
✓ User: John Doe (john.doe)
✓ Authentication working
```

### Step 5: Run First Scan

```cmd
run_scan.bat
```

The scanner will:
1. Connect to Jira
2. Count issues
3. Scan attachments (with progress bar)
4. Generate HTML report automatically

### Step 6: View Report

Open the HTML file in your browser:
```
reports\scan_XXXXXXXX_visual_analysis.html
```

---

## 🐧 Linux Installation

### Step 1: Extract Package

```bash
cd ~/Downloads
unzip Attachment-Architect-v1.0.zip
cd Attachment-Architect-v1.0
```

### Step 2: Run Setup

```bash
chmod +x setup.sh
./setup.sh
```

**What it does:**
- ✅ Checks Python 3 installation
- ✅ Creates virtual environment (`venv/`)
- ✅ Installs all dependencies
- ✅ Creates `.env` from template
- ✅ Creates folders: `reports/`, `scans/`, `logs/`

### Step 3: Configure Credentials

```bash
nano .env
```

Add your Jira details:
```env
JIRA_BASE_URL=https://your-jira-instance.com
JIRA_TOKEN=your_personal_access_token_here
```

Save and exit (Ctrl+X, then Y, then Enter)

### Step 4: Test Connection

```bash
chmod +x test_connection.sh
./test_connection.sh
```

### Step 5: Run First Scan

```bash
chmod +x run_scan.sh
./run_scan.sh
```

### Step 6: View Report

```bash
xdg-open reports/scan_XXXXXXXX_visual_analysis.html
```

---

## 🍎 macOS Installation

### Step 1: Extract Package

```bash
cd ~/Downloads
unzip Attachment-Architect-v1.0.zip
cd Attachment-Architect-v1.0
```

### Step 2: Run Setup

```bash
chmod +x setup.sh
./setup.sh
```

### Step 3: Configure Credentials

```bash
nano .env
```

Add your Jira details:
```env
JIRA_BASE_URL=https://your-jira-instance.com
JIRA_TOKEN=your_personal_access_token_here
```

### Step 4: Test Connection

```bash
chmod +x test_connection.sh
./test_connection.sh
```

### Step 5: Run First Scan

```bash
chmod +x run_scan.sh
./run_scan.sh
```

### Step 6: View Report

```bash
open reports/scan_XXXXXXXX_visual_analysis.html
```

---

## 🔧 Manual Installation (Advanced)

If the automated setup doesn't work, follow these manual steps:

### 1. Create Virtual Environment

```bash
python -m venv venv
```

### 2. Activate Virtual Environment

**Windows:**
```cmd
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Create Configuration

```bash
# Windows
copy .env.example .env

# Linux/Mac
cp .env.example .env
```

Edit `.env` with your credentials.

### 5. Create Folders

```bash
# Windows
mkdir reports scans logs

# Linux/Mac
mkdir -p reports scans logs
```

### 6. Test Connection

```bash
python test_connection.py
```

### 7. Run Scanner

```bash
python jira_dc_scanner.py
```

---

## 🐳 Docker Installation (Optional)

Coming in v1.1

---

## 🔍 Verification

After installation, verify everything is working:

### Check Python Version
```bash
python --version
# Should show 3.8 or higher
```

### Check Virtual Environment
```bash
# Windows
dir venv

# Linux/Mac
ls -la venv
```

### Check Dependencies
```bash
# Activate venv first
pip list
# Should show: requests, pyyaml, tqdm, python-dotenv
```

### Check Configuration
```bash
# Windows
type .env

# Linux/Mac
cat .env
# Should show your JIRA_BASE_URL and JIRA_TOKEN
```

### Check Folders
```bash
# Windows
dir

# Linux/Mac
ls -la
# Should see: reports/, scans/, logs/
```

---

## 🛠️ Troubleshooting

### Python Not Found

**Problem:** `python: command not found`

**Solution:**
- **Windows**: Install from [python.org](https://python.org)
- **Linux**: `sudo apt install python3 python3-venv`
- **macOS**: `brew install python3`

### Permission Denied (Linux/Mac)

**Problem:** `Permission denied` when running scripts

**Solution:**
```bash
chmod +x *.sh
```

### SSL Certificate Error

**Problem:** `SSL: CERTIFICATE_VERIFY_FAILED`

**Solution:**
Edit `config.yaml`:
```yaml
jira:
  verify_ssl: false  # Only for self-signed certificates
```

### Module Not Found

**Problem:** `ModuleNotFoundError: No module named 'requests'`

**Solution:**
```bash
# Activate venv first
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Then install
pip install -r requirements.txt
```

### Connection Failed

**Problem:** `Authentication failed`

**Solution:**
1. Check `.env` file has correct URL and token
2. Verify token hasn't expired
3. Test manually: `python test_connection.py`

---

## 📦 Package Structure After Installation

```
Attachment-Architect-v1.0/
├── venv/                    # Virtual environment (created by setup)
├── reports/                 # Generated reports (created by setup)
├── scans/                   # Scan database (created by setup)
├── logs/                    # Log files (created by setup)
├── .env                     # Your credentials (created from .env.example)
├── jira_dc_scanner.py       # Main scanner
├── generate_visual_analysis_report.py
├── generate_html_content.py
├── test_connection.py
├── config.yaml
├── requirements.txt
├── setup.bat / setup.sh
├── run_scan.bat / run_scan.sh
├── test_connection.bat / test_connection.sh
└── Documentation files
```

---

## 🔄 Updating

To update to a newer version:

1. **Backup your data:**
   ```bash
   # Backup .env and config.yaml
   copy .env .env.backup
   copy config.yaml config.yaml.backup
   
   # Backup scans database
   copy scans\scan.db scans\scan.db.backup
   ```

2. **Extract new version** to a new folder

3. **Copy your configuration:**
   ```bash
   copy .env.backup new-folder\.env
   copy config.yaml.backup new-folder\config.yaml
   ```

4. **Run setup** in new folder

5. **Copy database** (optional, to keep old scans):
   ```bash
   copy scans\scan.db.backup new-folder\scans\scan.db
   ```

---

## 🗑️ Uninstallation

To completely remove Attachment Architect:

### Windows
```cmd
# Delete the entire folder
rmdir /s /q "C:\Path\To\Attachment-Architect-v1.0"
```

### Linux/Mac
```bash
# Delete the entire folder
rm -rf ~/Path/To/Attachment-Architect-v1.0
```

**Note:** This removes all scans, reports, and configuration.

---

## ✅ Post-Installation

After successful installation:

1. ✅ Read **QUICKSTART.md** for usage guide
2. ✅ Review **README.md** for detailed documentation
3. ✅ Check **config.yaml** for advanced settings
4. ✅ Run your first scan
5. ✅ Explore the HTML report

---

## 📞 Support

If you encounter issues during installation:

1. Check this guide's troubleshooting section
2. Review **QUICKSTART.md** for common issues
3. Check logs in `./logs/scanner.log`
4. Verify Python version: `python --version`

---

## 🎉 Installation Complete!

You're ready to start analyzing your Jira storage!

**Next Steps:**
1. Run `test_connection.bat/.sh` to verify connection
2. Run `run_scan.bat/.sh` to start your first scan
3. Open the HTML report to see your results

**Happy Scanning!** 🚀

---

**Attachment Architect v1.0**  
**Installation Guide - January 23, 2025**
