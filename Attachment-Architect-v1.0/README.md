<div align="center">
  <img src="logo.png" alt="Attachment Architect" width="100"/>
  
  # Attachment Architect for Jira Data Center
  
  **Professional Pre-Migration Storage Analysis Tool**
  
  Analyze your Jira Data Center attachment storage before migrating to Cloud. Identify duplicates, optimize storage, and plan your migration with confidence.
  
  [![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](VERSION.txt)
  [![License](https://img.shields.io/badge/license-Commercial-green.svg)](LICENSE)
  [![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
  [![Jira](https://img.shields.io/badge/Jira%20DC-8.0+-blue.svg)](https://www.atlassian.com/software/jira)
</div>

---

## 🎯 Perfect for Cloud Migration Planning

Preparing to migrate from Jira Data Center to Cloud? **Attachment Architect** gives you a comprehensive pre-migration analysis of your attachment storage, helping you:

- 🔍 **Identify cleanup opportunities** before migration
- 💰 **Reduce migration costs** by removing duplicates
- 📊 **Plan storage requirements** for your Cloud instance
- 🎯 **Prioritize cleanup efforts** with actionable insights
- 📈 **Generate executive reports** for stakeholder approval

---

---

## ✨ Features

- 🔍 **Deep Storage Analysis** - Scan all attachments across your Jira instance
- 📊 **Visual Reports** - Interactive HTML reports with 6 analysis dimensions
- 🔥 **Heat Index** - Identify "Frozen Dinosaurs" (large, inactive files)
- 🚀 **High Performance** - Multi-threaded downloads, streaming hash calculation
- 💾 **Resume Capability** - Interrupt and resume scans anytime
- 🎯 **Duplicate Detection** - Find identical files wasting storage
- 📈 **Comprehensive Insights** - By project, file type, user, age, and status

---

## 🚀 Quick Start

### **Easy Mode: Use Launcher Scripts** ⭐ **RECOMMENDED**

**Windows users** - Just double-click or run these BAT files:

```cmd
1. setup.bat              # One-time setup
2. Edit .env              # Add your Jira credentials
3. test_connection.bat    # Verify connection
4. run_scan.bat           # Run the scan
```

**Linux/Mac users** - Run these SH files:

```bash
1. ./setup.sh             # One-time setup
2. Edit .env              # Add your Jira credentials
3. ./test_connection.sh   # Verify connection
4. ./run_scan.sh          # Run the scan
```

**✨ Benefits of using launcher scripts:**
- ✅ **No manual virtual environment activation** - Scripts handle it automatically
- ✅ **Error checking** - Validates setup before running
- ✅ **Clear messages** - Shows what's happening at each step
- ✅ **Resume support** - Use `run_scan.bat --resume SCAN_ID` to continue interrupted scans

---

### **Detailed Setup Steps**

#### 1. **Setup Environment**

**Windows:**
```cmd
setup.bat
```

**Linux/Mac:**
```bash
chmod +x setup.sh
./setup.sh
```

This automatically:
- Creates virtual environment
- Installs dependencies
- Creates `.env` from template
- Creates necessary folders

#### 2. **Configure Credentials**

Edit the `.env` file with your Jira credentials:

```env
# Jira Connection
JIRA_BASE_URL=https://your-jira-instance.com
JIRA_TOKEN=your_personal_access_token_here

# OR use username/password (less secure)
# JIRA_USERNAME=your_username
# JIRA_PASSWORD=your_password
```

**💡 Tip**: Personal Access Tokens are recommended for Jira DC 8.14+

#### 3. **Test Connection**

**Windows:**
```cmd
test_connection.bat
```

**Linux/Mac:**
```bash
./test_connection.sh
```

**Or manually:**
```bash
python test_connection.py
```

Expected output:
```
✓ Connected to Jira successfully!
✓ User: John Doe (john.doe)
✓ Authentication working
```

#### 4. **Run Scan**

**Windows:**
```cmd
run_scan.bat
```

**Linux/Mac:**
```bash
./run_scan.sh
```

**Or manually:**
```bash
python jira_dc_scanner.py
```

The scanner will:
1. ✅ Connect to Jira
2. 📊 Count total issues
3. 🔄 Scan attachments (with progress bar)
4. 💾 Save results to `./reports/scan_XXXXXXXX.json`
5. 📈 **Automatically generate HTML visual report**
6. 🎉 Display summary and report path

#### 5. **View Report**

Open the generated HTML file in your browser:
```
./reports/scan_XXXXXXXX_visual_analysis.html
```

---

### **Advanced: Resume Interrupted Scans**

If your scan is interrupted, you can easily resume:

**Windows:**
```cmd
run_scan.bat --resume SCAN_ID
```

**Linux/Mac:**
```bash
./run_scan.sh --resume SCAN_ID
```

**Or manually:**
```bash
python jira_dc_scanner.py --resume SCAN_ID
```

---

## 📖 Detailed Usage

### Configuration Options

Edit `config.yaml` to customize scan behavior:

```yaml
jira:
  base_url: "https://your-jira.com"
  verify_ssl: true

scan:
  batch_size: 100              # Issues per batch
  thread_pool_size: 12         # Parallel downloads
  rate_limit_per_second: 50    # API requests/sec
  use_content_hash: true       # Hash file content (vs URL)
  max_file_size_gb: 5          # Skip files larger than this
  download_timeout_seconds: 300

filters:
  # Scan specific projects only
  projects: []                 # Empty = all projects
  
  # Date range
  date_from: ""                # Format: YYYY-MM-DD
  date_to: ""                  # Format: YYYY-MM-DD
  
  # OR use custom JQL
  custom_jql: ""               # Overrides all other filters

output:
  output_dir: "./reports"

storage:
  database_path: "./scans/scan.db"
  checkpoint_interval: 100     # Save progress every N issues

logging:
  level: "INFO"
  file: "./logs/scanner.log"
  console: true
```

### Resume Interrupted Scan

If a scan is interrupted (Ctrl+C, network issue, etc.):

```bash
python jira_dc_scanner.py --resume SCAN_ID
```

Example:
```bash
python jira_dc_scanner.py --resume 9f7629d1
```

### Generate Report from Existing Scan

```bash
python generate_visual_analysis_report.py scan_9f7629d1.json
```

**Customize "Frozen Dinosaurs" criteria:**

```bash
# Files > 5 MB inactive for > 180 days
python generate_visual_analysis_report.py scan_9f7629d1.json --min-size 5 --min-days 180
```

---

## 📊 Visual Report Features

The HTML report includes **6 interactive tabs**:

### 1. 📊 **By Project**
- Storage consumption per project
- File counts and average sizes
- Color-coded by file size

### 2. 🔍 **By File Type**
- Top file types by storage
- File counts per extension
- Identify storage-heavy formats

### 3. 👥 **By User**
- Top 10 storage consumers
- Format: `Name Surname (username)`
- Files uploaded per user

### 4. 📅 **By Age**
- Attachment age distribution
- Buckets: 0-90 days, 90-365 days, 1-2 years, 2-4 years, >4 years
- Identify archival candidates

### 5. 📋 **By Status**
- Storage by issue status
- Format: `Status Name (ID: X)` *(when available)*
- Find storage in closed/resolved issues

### 6. 🔥 **Heat Index**
- **"Frozen Dinosaurs"**: Large files on inactive issues
- **Sortable table**: Click any column header to sort
- **Search & filter**: Find specific files
- **Pagination**: Browse all files efficiently

---

## 🔧 Advanced Features

### Custom JQL Queries

Scan specific issues using custom JQL:

```yaml
# config.yaml
filters:
  custom_jql: "project = MYPROJECT AND created >= -365d"
```

### Performance Tuning

For large instances (>100K issues):

```yaml
scan:
  batch_size: 50               # Smaller batches
  thread_pool_size: 8          # Fewer threads
  rate_limit_per_second: 30    # Lower rate limit
```

For small instances (<10K issues):

```yaml
scan:
  batch_size: 200              # Larger batches
  thread_pool_size: 20         # More threads
  rate_limit_per_second: 100   # Higher rate limit
```

### URL-Based Hashing (Faster)

Skip content downloads, hash URLs instead:

```yaml
scan:
  use_content_hash: false      # Much faster, less accurate
```

**Trade-off**: Files with identical content but different URLs won't be detected as duplicates.

---

## 📁 Project Structure

```
Attachment-Architect_python/
├── jira_dc_scanner.py              # Main scanner
├── generate_visual_analysis_report.py  # Report generator
├── generate_html_content.py        # HTML template
├── test_connection.py              # Connection tester
├── config.yaml                     # Configuration
├── .env                            # Credentials (create from .env.example)
├── requirements.txt                # Python dependencies
├── README.md                       # This file
├── reports/                        # Generated reports
│   ├── scan_XXXXXXXX.json
│   └── scan_XXXXXXXX_visual_analysis.html
├── scans/                          # Scan database
│   └── scan.db
└── logs/                           # Log files
    └── scanner.log
```

---

## 🛠️ Troubleshooting

### Connection Issues

**Problem**: `Authentication failed`

**Solution**:
1. Verify credentials in `.env`
2. For Personal Access Token: Check token hasn't expired
3. For username/password: Verify credentials are correct
4. Run `python test_connection.py` to diagnose

---

**Problem**: `SSL Certificate verification failed`

**Solution**:
```yaml
# config.yaml
jira:
  verify_ssl: false  # Only for self-signed certificates
```

---

### Performance Issues

**Problem**: Scan is very slow

**Solutions**:
1. **Reduce thread pool size** if network is slow:
   ```yaml
   scan:
     thread_pool_size: 6
   ```

2. **Use URL-based hashing** (faster but less accurate):
   ```yaml
   scan:
     use_content_hash: false
   ```

3. **Increase rate limit** if Jira server can handle it:
   ```yaml
   scan:
     rate_limit_per_second: 100
   ```

---

**Problem**: Scan keeps timing out

**Solution**:
```yaml
scan:
  download_timeout_seconds: 600  # Increase timeout
  max_file_size_gb: 2            # Skip very large files
```

---

### Memory Issues

**Problem**: Out of memory errors

**Solution**:
```yaml
scan:
  batch_size: 50                 # Smaller batches
  thread_pool_size: 6            # Fewer threads
  checkpoint_interval: 50        # Save more frequently
```

---

### Resume Not Working

**Problem**: Can't resume scan

**Solution**:
1. Check scan ID is correct (8 characters)
2. Verify `./scans/scan.db` exists
3. Check logs in `./logs/scanner.log`

---

## 📋 Requirements

- **Python**: 3.8 or higher
- **Jira**: Data Center 8.0 or higher
- **Permissions**: Read access to issues and attachments
- **Network**: Access to Jira instance
- **Disk Space**: ~100 MB per 100K attachments (for database)

---

## 🔒 Security Notes

1. **Never commit `.env` file** - Contains sensitive credentials
2. **Use Personal Access Tokens** - More secure than username/password
3. **Limit token permissions** - Read-only access is sufficient
4. **Rotate tokens regularly** - Best practice for security
5. **Use SSL verification** - Only disable for trusted self-signed certs

---

## 📝 License

Commercial License - Attachment Architect Team

---

## 🤝 Support

For issues, questions, or feature requests:
1. Check the troubleshooting section above
2. Review logs in `./logs/scanner.log`
3. Contact support with scan ID and error details

---

## 🎯 Best Practices

### Before Scanning

1. ✅ Test connection first: `python test_connection.py`
2. ✅ Start with a small project to test
3. ✅ Review `config.yaml` settings
4. ✅ Ensure sufficient disk space

### During Scanning

1. 💡 Monitor progress bar and metrics
2. 💡 Check logs if issues occur
3. 💡 Don't interrupt unless necessary (use Ctrl+C to save checkpoint)

### After Scanning

1. 📊 Review visual report in browser
2. 📊 Identify "Frozen Dinosaurs" for archival
3. 📊 Share report with stakeholders
4. 📊 Plan cleanup based on insights

---

## 🚀 Quick Reference

```bash
# Setup
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt

# Configure
copy .env.example .env
# Edit .env with your credentials

# Test
python test_connection.py

# Scan
python jira_dc_scanner.py

# Resume
python jira_dc_scanner.py --resume SCAN_ID

# Generate report
python generate_visual_analysis_report.py scan_XXXXXXXX.json

# Custom report
python generate_visual_analysis_report.py scan_XXXXXXXX.json --min-size 5 --min-days 180
```

---

**Made with ❤️ by Attachment Architect Team**
