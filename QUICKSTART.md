# 🚀 Quick Start Guide

Get up and running with the Jira Data Center Attachment Analysis Tool in 5 minutes.

## Prerequisites

- Python 3.8+ installed
- Access to Jira Data Center instance
- Personal Access Token or username/password

## Step 1: Setup (2 minutes)

### Windows

```cmd
setup.bat
```

### Linux/Mac

```bash
chmod +x setup.sh
./setup.sh
```

This will:
- Create a virtual environment
- Install all dependencies
- Create necessary directories
- Copy `.env.example` to `.env`

## Step 2: Configure (1 minute)

Edit the `.env` file with your Jira credentials:

```env
JIRA_BASE_URL=https://jira.yourcompany.com
JIRA_TOKEN=your_personal_access_token_here
```

### How to Get a Personal Access Token

1. Log in to your Jira Data Center instance
2. Click your profile icon → **Personal Access Tokens**
3. Click **Create token**
4. Enter a name (e.g., "Attachment Scanner")
5. Set expiration (or leave blank for no expiration)
6. Click **Create**
7. **Copy the token** (you won't see it again!)
8. Paste it into the `.env` file

## Step 3: Test Connection (30 seconds)

Verify your configuration works:

```bash
# Windows
venv\Scripts\activate
python test_connection.py

# Linux/Mac
source venv/bin/activate
python test_connection.py
```

You should see:
```
✓ Connected to Jira successfully!
✓ User: John Doe (john.doe@company.com)
✓ Jira Version: 9.12.0
```

## Step 4: Run Your First Scan (1 minute)

Start a scan of your Jira instance:

```bash
python jira_dc_scanner.py
```

You'll see real-time progress:

```
Analyzing Issues: [████████░░░░░░░░░░░░] 40% | 4,000/10,000 [00:02:15<00:03:22]
files: 2,134 | dupes: 456 | waste: 1.23 GB
```

## Step 5: View Results (30 seconds)

After the scan completes, check the `./reports` directory:

```
reports/
  └── scan_abc123.json    # Complete scan data
```

The console will also show a summary:

```
======================================================================
SCAN SUMMARY
======================================================================
Scan ID: abc123
Duration: 185.4 seconds
Issues Processed: 10,000

Total Files: 5,234
Total Storage: 15.67 GB

Duplicate Files: 1,456
Duplicate Storage: 2.34 GB
Waste Percentage: 14.9%
======================================================================
```

## Common Scenarios

### Scan Specific Projects Only

Edit `config.yaml`:

```yaml
filters:
  projects: ["MYPROJECT", "ANOTHERPROJECT"]
```

### Scan Recent Issues Only

Edit `config.yaml`:

```yaml
filters:
  date_from: "2024-01-01"
```

### Faster Scanning (URL-based hashing)

Edit `config.yaml`:

```yaml
scan:
  use_content_hash: false  # Faster but less accurate
```

### Resume Interrupted Scan

If your scan is interrupted, resume it:

```bash
python jira_dc_scanner.py --resume --scan-id abc123
```

## Troubleshooting

### "Authentication failed"

- Check your Personal Access Token is correct
- Verify the token hasn't expired
- Try using username/password instead:

```env
JIRA_USERNAME=your_username
JIRA_PASSWORD=your_password
```

### "Connection error"

- Verify `JIRA_BASE_URL` is correct (no trailing slash)
- Check network connectivity to Jira server
- If using HTTPS with self-signed cert, set in `config.yaml`:

```yaml
jira:
  verify_ssl: false
```

### "Permission denied"

- Ensure your user has "Browse Projects" permission
- For full-instance scans, you may need admin access

### Scan is slow

- Run the script on a server in the same LAN as Jira
- Increase thread pool size in `config.yaml`:

```yaml
scan:
  thread_pool_size: 16  # Default is 12
```

## Next Steps

- Read the full [README.md](README.md) for detailed documentation
- Review [JIRA_DC_ANALYSIS_DESIGN.md](JIRA_DC_ANALYSIS_DESIGN.md) for architecture details
- Customize `config.yaml` for your needs
- Schedule regular scans with cron/Task Scheduler

## Support

If you encounter issues:

1. Check `./logs/scanner.log` for detailed error messages
2. Review the [Troubleshooting](README.md#troubleshooting) section in README
3. Contact the Attachment Architect team

---

**Happy scanning! 🎉**
