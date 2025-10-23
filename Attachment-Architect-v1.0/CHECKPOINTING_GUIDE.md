# 🔄 Checkpointing & Resume Guide

## How Checkpointing Works

The scanner automatically saves progress every **100 issues** (configurable) to a SQLite database located at `./scans/scan.db`.

### What Gets Saved

1. **Scan State** - Scan ID, progress, timestamps
2. **Scan Statistics** - File counts, storage totals, project stats
3. **Duplicate Groups** - All detected duplicates and their locations
4. **Checkpoint** - Last processed position for resume

### Automatic Checkpointing

Checkpoints are saved:
- ✅ Every 100 issues (default, configurable in `config.yaml`)
- ✅ When you press **Ctrl+C** (graceful interruption)
- ✅ On scan completion

---

## Current Resume Functionality

### Manual Resume (Currently Implemented)

If a scan is interrupted, you can resume it manually:

```bash
# Find your scan ID from the output or database
python jira_dc_scanner.py --resume SCAN_ID
```

**Example:**
```bash
python jira_dc_scanner.py --resume 9f7629d1
```

### What Happens on Resume

1. Loads checkpoint from database
2. Restores scan state and statistics
3. Continues from last processed issue
4. Maintains all duplicate detection data

---

## Proposed Enhancements

### 1. Auto-Resume (Recommended)

**Behavior:**
- Scanner detects incomplete scans automatically
- Prompts user: "Found incomplete scan 9f7629d1. Resume? (Y/n)"
- If yes, resumes automatically
- If no, starts new scan

**Implementation:**
```python
# Check for incomplete scans on startup
def check_for_incomplete_scans(storage_manager):
    cursor = storage_manager.conn.cursor()
    cursor.execute('''
        SELECT scan_id, start_time, processed_issues, total_issues 
        FROM scans 
        WHERE status = 'running' 
        ORDER BY start_time DESC 
        LIMIT 1
    ''')
    row = cursor.fetchone()
    
    if row:
        scan_id = row['scan_id']
        progress = (row['processed_issues'] / row['total_issues']) * 100
        print(f"\n⚠️  Found incomplete scan: {scan_id}")
        print(f"   Progress: {row['processed_issues']}/{row['total_issues']} ({progress:.1f}%)")
        print(f"   Started: {row['start_time']}")
        
        response = input("\nResume this scan? (Y/n): ").strip().lower()
        if response in ['', 'y', 'yes']:
            return scan_id
    
    return None
```

### 2. Reset Functionality

**Add `--reset` flag:**

```bash
# Start fresh, ignoring any incomplete scans
python jira_dc_scanner.py --reset

# Or reset specific scan
python jira_dc_scanner.py --reset SCAN_ID
```

**Implementation:**
```python
parser.add_argument('--reset', nargs='?', const=True, metavar='SCAN_ID',
                   help='Reset scan (delete checkpoint and start fresh)')

# In main():
if args.reset:
    if args.reset is True:
        # Reset all incomplete scans
        storage_manager.reset_all_incomplete_scans()
    else:
        # Reset specific scan
        storage_manager.reset_scan(args.reset)
    print("✓ Scan data reset. Starting fresh...")
```

### 3. List Scans Command

**Add `--list` flag:**

```bash
# List all scans
python jira_dc_scanner.py --list
```

**Output:**
```
Available Scans:
================
1. 9f7629d1 - Running (75% complete)
   Started: 2025-01-23 10:30:00
   Progress: 7500/10000 issues
   
2. 8a5b3c2d - Completed
   Started: 2025-01-22 14:00:00
   Duration: 45 minutes
   Files: 5000, Storage: 2.5 GB
```

---

## Configuration

### Checkpoint Interval

Edit `config.yaml`:

```yaml
storage:
  database_path: "./scans/scan.db"
  checkpoint_interval: 100  # Save every N issues
```

**Recommendations:**
- **Small instances** (<10K issues): 50-100
- **Medium instances** (10K-100K): 100-200
- **Large instances** (>100K): 200-500

### Database Location

Change database path if needed:

```yaml
storage:
  database_path: "./my_scans/scan.db"
```

---

## Troubleshooting

### "No checkpoint found"

**Problem:** Trying to resume a scan that doesn't exist.

**Solution:**
```bash
# List available scans
python jira_dc_scanner.py --list

# Use correct scan ID
python jira_dc_scanner.py --resume CORRECT_SCAN_ID
```

### Corrupted Database

**Problem:** Database file is corrupted.

**Solution:**
```bash
# Backup old database
mv ./scans/scan.db ./scans/scan.db.backup

# Start fresh
python jira_dc_scanner.py
```

### Resume from Wrong Position

**Problem:** Resume starts from wrong position.

**Solution:**
```bash
# Reset and start fresh
python jira_dc_scanner.py --reset SCAN_ID
```

---

## Best Practices

### 1. Regular Checkpoints
- Keep checkpoint_interval at 100 for most cases
- Lower for unstable networks
- Higher for very large instances

### 2. Monitor Progress
- Check logs in `./logs/scanner.log`
- Progress bar shows real-time status
- Checkpoints logged every save

### 3. Graceful Interruption
- Use **Ctrl+C** to stop (saves checkpoint)
- Don't kill process forcefully
- Wait for "Checkpoint saved" message

### 4. Database Backup
```bash
# Before major scans
cp ./scans/scan.db ./scans/scan.db.backup
```

---

## Implementation Status

### ✅ Currently Implemented
- [x] Automatic checkpointing every 100 issues
- [x] Checkpoint on Ctrl+C
- [x] Manual resume with `--resume SCAN_ID`
- [x] Full state restoration
- [x] Progress tracking

### 🔄 Proposed Enhancements
- [ ] Auto-detect incomplete scans
- [ ] Prompt user to resume
- [ ] `--reset` flag to start fresh
- [ ] `--list` flag to show all scans
- [ ] Auto-cleanup old scans

---

## Quick Reference

```bash
# Start new scan
python jira_dc_scanner.py

# Resume specific scan
python jira_dc_scanner.py --resume SCAN_ID

# Reset and start fresh (proposed)
python jira_dc_scanner.py --reset

# List all scans (proposed)
python jira_dc_scanner.py --list

# Interrupt scan gracefully
Ctrl+C (saves checkpoint automatically)
```

---

## Database Schema

The checkpoint system uses 4 tables:

1. **scans** - Scan metadata and state
2. **scan_stats** - Statistics (files, storage, etc.)
3. **duplicate_groups** - Detected duplicates
4. **checkpoints** - Resume points

**Location:** `./scans/scan.db` (SQLite)

**View database:**
```bash
sqlite3 ./scans/scan.db
.tables
SELECT * FROM scans;
.quit
```

---

**Current Version: 1.0.0**
**Checkpointing: Fully Functional**
**Auto-Resume: Proposed Enhancement**
