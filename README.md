# 🏢 Jira Data Center Attachment Analysis Tool

A high-performance Python tool for analyzing attachments in Jira Data Center (versions 9 and 10) to identify duplicates and storage waste.

## Features

✅ **Multi-threaded Performance** - Downloads and analyzes files in parallel  
✅ **Content-based Hashing** - Accurate duplicate detection using SHA-256  
✅ **Resume Capability** - Checkpoint system allows resuming interrupted scans  
✅ **Real-time Progress** - Live progress bars and statistics  
✅ **Comprehensive Analysis** - Statistics by project, file type, user, and more  
✅ **Multiple Export Formats** - JSON, CSV, Excel, and HTML reports  
✅ **Configurable Filters** - Filter by project, date range, file type, etc.  

## Performance

| Instance Size | Issues | Attachments | Estimated Time |
|--------------|--------|-------------|----------------|
| Small | 1,000 | 500 | 2-3 minutes |
| Medium | 10,000 | 5,000 | 15-20 minutes |
| Large | 100,000 | 50,000 | 2-3 hours |
| Enterprise | 500,000 | 250,000 | 10-15 hours |

*Performance assumes LAN deployment with 1 Gbps network connection*

## Requirements

- Python 3.8 or higher
- Network access to Jira Data Center server
- Jira user account with appropriate permissions
- Personal Access Token (recommended) or username/password

### Jira Permissions Required

- **Browse Projects** permission
- **View Issues** permission
- **Admin access** (recommended for full-instance scans)

## Installation

### 1. Clone or Download

```bash
cd "c:\Users\krozenbe\Documents\Jira plugins\Attachment-Architect_python"
```

### 2. Create Virtual Environment (Recommended)

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

Copy the example environment file and fill in your Jira details:

```bash
copy .env.example .env
```

Edit `.env` file:

```env
JIRA_BASE_URL=https://jira.yourcompany.com
JIRA_TOKEN=your_personal_access_token_here
```

**How to get a Personal Access Token:**
1. Log in to Jira Data Center
2. Go to Profile → Personal Access Tokens
3. Click "Create token"
4. Give it a name and set expiration
5. Copy the token (you won't see it again!)

## Usage

### Basic Scan

Run a full scan of your Jira instance:

```bash
python jira_dc_scanner.py
```

### Configuration

Edit `config.yaml` to customize the scan:

```yaml
scan:
  batch_size: 100              # Issues per API call
  thread_pool_size: 12         # Parallel download workers
  max_file_size_gb: 5          # Skip files larger than this
  use_content_hash: true       # Hash actual content (vs URL)

filters:
  projects: ["PROJ", "TEST"]   # Specific projects (empty = all)
  date_from: "2023-01-01"      # Start date (null = no limit)
  date_to: "2024-12-31"        # End date (null = no limit)
  file_types: ["pdf", "png"]   # File types (empty = all)
```

### Resume Interrupted Scan

If a scan is interrupted, you can resume it:

```bash
python jira_dc_scanner.py --resume --scan-id abc123
```

## Output

### Console Output

During the scan, you'll see real-time progress:

```
Analyzing Issues: [████████████████████] 100% | 10,000/10,000 [00:15:23<00:00]
files: 5,234 | dupes: 1,456 | waste: 2.34 GB
```

### Scan Summary

After completion, a summary is displayed:

```
======================================================================
SCAN SUMMARY
======================================================================
Scan ID: abc123
Duration: 923.4 seconds
Issues Processed: 10,000

Total Files: 5,234
Total Storage: 15.67 GB

Canonical Files: 3,778
Duplicate Files: 1,456
Duplicate Storage: 2.34 GB
Waste Percentage: 14.9%

======================================================================
QUICK WINS (Top 3 Duplicate Files)
======================================================================

1. large-report.pdf
   File Size: 45.23 MB
   Duplicates: 23
   Wasted Space: 1.04 GB

2. screenshot.png
   File Size: 2.34 MB
   Duplicates: 156
   Wasted Space: 365.04 MB

3. design-mockup.psd
   File Size: 89.12 MB
   Duplicates: 4
   Wasted Space: 356.48 MB
======================================================================
```

### Reports

Reports are saved to the `./reports` directory:

- **JSON**: `scan_abc123.json` - Complete scan data
- **CSV**: `scan_abc123.csv` - Tabular data for Excel
- **Excel**: `scan_abc123.xlsx` - Formatted spreadsheet with charts
- **HTML**: `scan_abc123.html` - Interactive web report

### Database

Scan data is stored in SQLite database at `./scans/scan.db`:

- Persistent storage of all scan results
- Enables resume capability
- Allows comparison between scans
- Can be queried with SQL tools

## Architecture

### Key Components

1. **JiraDataCenterClient** - API v2 client with authentication and rate limiting
2. **DownloadManager** - Multi-threaded parallel download engine
3. **StreamingHasher** - Memory-efficient hash calculation
4. **StorageManager** - SQLite-based persistence with checkpoints
5. **AttachmentScanner** - Main orchestrator

### Performance Optimizations

- **Multi-threading**: 12 parallel download workers (configurable)
- **Streaming**: Files never fully loaded into memory
- **Batching**: Processes 100 issues per API call
- **Checkpointing**: Saves progress every 100 issues
- **Rate Limiting**: Configurable to match server capacity

## Troubleshooting

### Connection Errors

```
ERROR: Failed to connect to Jira. Check your credentials.
```

**Solutions:**
- Verify `JIRA_BASE_URL` is correct (no trailing slash)
- Check Personal Access Token is valid and not expired
- Ensure network connectivity to Jira server
- Verify SSL certificate if using HTTPS

### Permission Errors

```
ERROR: Permission denied. Check API token permissions.
```

**Solutions:**
- Ensure user has "Browse Projects" permission
- Check user can view issues in target projects
- For full-instance scans, admin access may be required

### Rate Limit Errors

```
ERROR: Rate limit exceeded. Please wait and try again.
```

**Solutions:**
- Reduce `rate_limit_per_second` in `config.yaml`
- Increase `thread_pool_size` to process more in parallel
- Contact Jira admin to increase rate limits

### Memory Issues

```
ERROR: Out of memory
```

**Solutions:**
- Reduce `thread_pool_size` (fewer parallel downloads)
- Reduce `batch_size` (fewer issues per batch)
- Set `max_file_size_gb` lower to skip large files
- Run on machine with more RAM

### Slow Performance

**Optimizations:**
- Run on server in same LAN as Jira (critical!)
- Increase `thread_pool_size` (if CPU/network allows)
- Increase `rate_limit_per_second` (if server allows)
- Set `use_content_hash: false` for faster URL-based hashing

## Advanced Usage

### Custom JQL Queries

Edit `config.yaml` to use custom filters:

```yaml
filters:
  projects: ["MYPROJECT"]
  date_from: "2024-01-01"
  file_types: ["pdf", "docx"]
```

### Database Queries

Query the SQLite database directly:

```bash
sqlite3 ./scans/scan.db

# List all scans
SELECT scan_id, status, processed_issues, duration_ms 
FROM scans 
ORDER BY start_time DESC;

# Get duplicate files for a scan
SELECT file_name, file_size, duplicate_count, total_wasted_space
FROM duplicate_groups
WHERE scan_id = 'abc123' AND duplicate_count > 0
ORDER BY total_wasted_space DESC
LIMIT 10;
```

### Export to CSV

```python
import sqlite3
import pandas as pd

conn = sqlite3.connect('./scans/scan.db')
df = pd.read_sql_query("""
    SELECT file_name, file_size, duplicate_count, total_wasted_space
    FROM duplicate_groups
    WHERE scan_id = 'abc123' AND duplicate_count > 0
    ORDER BY total_wasted_space DESC
""", conn)

df.to_csv('duplicates.csv', index=False)
```

## Comparison: Cloud vs Data Center

| Feature | Cloud (Forge) | Data Center (Python) |
|---------|---------------|---------------------|
| API Version | v3 | v2 |
| Authentication | OAuth 2.0 | Personal Access Token |
| Hash Method | URL-based | Content-based |
| Network | Internet | LAN (much faster) |
| Rate Limit | 10 req/sec | 50-100+ req/sec |
| Storage | 240KB limit | Unlimited (SQLite) |
| Deployment | Cloud-hosted | On-premise |
| Resume | Automatic | Checkpoint-based |

## Development

### Running Tests

```bash
pytest tests/
```

### Code Formatting

```bash
black jira_dc_scanner.py
flake8 jira_dc_scanner.py
```

### Logging

Logs are written to `./logs/scanner.log`. Adjust log level in `config.yaml`:

```yaml
logging:
  level: DEBUG  # DEBUG, INFO, WARNING, ERROR
  console: true
```

## Support

For issues, questions, or feature requests:

1. Check the [Troubleshooting](#troubleshooting) section
2. Review the logs in `./logs/scanner.log`
3. Contact the Attachment Architect team

## License

Commercial - Attachment Architect Team

## Version History

### 1.0.0 (January 2025)
- Initial release
- Multi-threaded scanning
- Content-based hashing
- Checkpoint/resume capability
- SQLite storage
- JSON export
- Real-time progress reporting

## Roadmap

### Phase 2 (Planned)
- CSV and Excel export
- HTML report generation
- Comparison mode (compare two scans)
- Dry-run mode

### Phase 3 (Planned)
- Advanced filtering options
- User-based analysis
- Age-based analysis
- Status-based analysis
- Automated cleanup recommendations

---

**Built with ❤️ for Jira Data Center administrators**
