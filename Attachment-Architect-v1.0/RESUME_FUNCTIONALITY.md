# Resume Functionality Guide

## Overview

The Attachment Architect scanner now includes **automatic resume detection** when running `run_scan.bat` or `run_scan.sh`. If an interrupted scan is detected, you'll be prompted to resume it, start a new scan, or delete the interrupted scan.

## How It Works

### Automatic Checkpoint Saving

The scanner automatically saves progress:
- **Every 100 issues** (configurable in `config.yaml`)
- **On interruption** (Ctrl+C)
- **On error/crash**

### What Gets Saved

- Scan state (scan_id, progress, timestamps)
- All duplicate groups found so far
- Statistics (file counts, sizes, etc.)
- Last processed position

### Storage Location

All scan data is stored in: `./scans/scan.db` (SQLite database)

## Using run_scan.bat / run_scan.sh

### Scenario 1: No Interrupted Scans

```bash
run_scan.bat
```

The scanner starts normally with no prompts.

### Scenario 2: Interrupted Scan Detected

```bash
run_scan.bat
```

You'll see:

```
========================================
INCOMPLETE SCAN DETECTED
========================================
Scan ID: 9f7629d1

An interrupted scan was found. Would you like to:
  [R] Resume the interrupted scan
  [N] Start a new scan (previous scan will remain in database)
  [D] Delete the interrupted scan and start fresh

Your choice (R/N/D):
```

**Options:**

- **R (Resume)**: Continues from where the scan was interrupted
  - Loads all previously found duplicates
  - Continues from the last processed issue
  - Maintains the same scan ID

- **N (New)**: Starts a fresh scan
  - Creates a new scan ID
  - Previous scan data remains in database
  - You can resume the old scan later using `--resume`

- **D (Delete)**: Removes the interrupted scan and starts fresh
  - Deletes all data for the interrupted scan
  - Starts a completely new scan
  - Cannot be undone

## Command-Line Options

### Resume a Specific Scan

```bash
python jira_dc_scanner.py --resume <scan_id>
```

Example:
```bash
python jira_dc_scanner.py --resume 9f7629d1
```

### List All Scans

```bash
python jira_dc_scanner.py --list
```

Output:
```
========================================
ALL SCANS
========================================

Scan ID: 9f7629d1
  Status: running
  Started: 2024-01-15T10:30:00
  Progress: 450/1000 issues
  Files: 2,345 (1.2 GB)

Scan ID: 8e5421a3
  Status: completed
  Started: 2024-01-14T09:00:00
  Completed: 2024-01-14T09:45:00
  Duration: 2700.0s
  Progress: 1000/1000 issues
  Files: 5,678 (3.4 GB)
```

### Reset All Incomplete Scans

```bash
python jira_dc_scanner.py --reset
```

This deletes ALL incomplete scans from the database.

### Reset a Specific Scan

```bash
python jira_dc_scanner.py --reset <scan_id>
```

Example:
```bash
python jira_dc_scanner.py --reset 9f7629d1
```

### Cleanup Old Completed Scans

```bash
python jira_dc_scanner.py --cleanup
```

Deletes completed scans older than 30 days (default).

To specify a different number of days:
```bash
python jira_dc_scanner.py --cleanup 60
```

## Finding Your Scan ID

### Method 1: From Console Output

When a scan starts, the scan ID is printed:
```
Starting scan 9f7629d1
```

### Method 2: Using --list Command

```bash
python jira_dc_scanner.py --list
```

### Method 3: Direct Database Query

```bash
sqlite3 ./scans/scan.db "SELECT scan_id, status, processed_issues, total_issues FROM scans;"
```

## Configuration

### Checkpoint Interval

Edit `config.yaml` to change how often checkpoints are saved:

```yaml
storage:
  checkpoint_interval: 100  # Save every 100 issues (default)
```

Lower values = more frequent saves = slower performance but safer
Higher values = less frequent saves = faster performance but more data loss on crash

### Database Location

Edit `config.yaml` to change where scan data is stored:

```yaml
storage:
  database_path: './scans/scan.db'  # Default location
```

## Troubleshooting

### "No checkpoint found for scan X"

The scan ID doesn't exist or was deleted. Use `--list` to see available scans.

### "Scan state not found for scan X"

The scan was partially deleted. Use `--reset <scan_id>` to clean it up.

### Multiple Incomplete Scans

If you have multiple interrupted scans, `run_scan.bat` will prompt for the most recent one. Use `--list` to see all scans and `--resume <scan_id>` to resume a specific one.

### Database Corruption

If the database becomes corrupted:

1. Backup the database: `copy scans\scan.db scans\scan.db.backup`
2. Delete the database: `del scans\scan.db`
3. Start a fresh scan

## Best Practices

1. **Let scans complete naturally** - The scanner is designed to handle interruptions, but completing scans is always better

2. **Use Ctrl+C to interrupt** - This triggers a clean checkpoint save before exiting

3. **Don't delete scan.db while scanning** - This will cause data loss

4. **Regular cleanup** - Use `--cleanup` periodically to remove old completed scans

5. **Monitor disk space** - The database grows with the number of attachments scanned

## Technical Details

### Database Schema

The scanner uses SQLite with 4 main tables:

- **scans**: Scan metadata and state
- **scan_stats**: Aggregated statistics
- **duplicate_groups**: Duplicate file information
- **checkpoints**: Resume points

### Resume Process

When resuming:

1. Load scan state from database
2. Load all previously found duplicate groups
3. Load statistics
4. Continue from last processed issue index
5. Merge new results with existing data

### Data Integrity

- All database operations use transactions
- Checkpoints are atomic (all-or-nothing)
- Failed checkpoints don't corrupt existing data

## Examples

### Example 1: Resume After Ctrl+C

```bash
# Start scan
run_scan.bat

# Press Ctrl+C after processing 500 issues
^C
Scan interrupted by user.

# Run again
run_scan.bat

# Choose [R] to resume
Your choice (R/N/D): R

# Scan continues from issue 500
```

### Example 2: Multiple Scans

```bash
# Start scan A
run_scan.bat
# Interrupt with Ctrl+C

# Start scan B (choose [N] for new)
run_scan.bat
Your choice (R/N/D): N

# Now you have 2 incomplete scans
python jira_dc_scanner.py --list

# Resume scan A specifically
python jira_dc_scanner.py --resume <scan_a_id>
```

### Example 3: Clean Start

```bash
# Delete all incomplete scans
python jira_dc_scanner.py --reset

# Start fresh
run_scan.bat
```

## Support

For issues or questions:
1. Check the logs in `./logs/scanner.log`
2. Use `--list` to inspect scan states
3. Try `--reset` to clean up problematic scans
4. Contact support with your scan ID and error messages
