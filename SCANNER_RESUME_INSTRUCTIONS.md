# Scanner Resume Functionality

## Current Status

The scanner **ALREADY HAS** checkpoint/resume functionality built-in:

### ✅ What Works Now:

1. **Automatic Checkpointing**
   - Saves progress every 100 issues (configurable in `config.yaml`)
   - Saves on interruption (Ctrl+C)
   - Saves on error

2. **Data Saved:**
   - Scan state (scan_id, progress, timestamps)
   - All duplicate groups found
   - Statistics
   - Last processed position

3. **Database:**
   - Location: `./scans/scan.db`
   - Contains: scans, scan_stats, duplicate_groups, checkpoints tables

### ❌ What's Missing:

**Command-line interface to resume** - The `scanner.scan(resume=True, scan_id='xxx')` function exists but there's no CLI argument to trigger it.

## How to Add Resume CLI

Add this code to the `main()` function at the very beginning (after the docstring):

```python
def main():
    """Main entry point."""
    import argparse
    
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Jira Attachment Scanner')
    parser.add_argument('--resume', metavar='SCAN_ID', help='Resume scan from checkpoint')
    args = parser.parse_args()
    
    print("="*70)
    print("Jira Data Center Attachment Analysis Tool")
    # ... rest of the code
```

Then change this line (around line 1450):

```python
# OLD:
results = scanner.scan()

# NEW:
if args.resume:
    print(f"\nResuming scan {args.resume}...\n")
    results = scanner.scan(resume=True, scan_id=args.resume)
else:
    print("\nStarting new scan...\n")
    results = scanner.scan()
```

## Usage After Fix:

```bash
# Start new scan
python jira_dc_scanner.py

# Resume interrupted scan
python jira_dc_scanner.py --resume 9f7629d1
```

## Finding Scan ID:

The scan ID is printed when the scan starts:
```
Starting scan 9f7629d1
```

Or check the database:
```bash
sqlite3 ./scans/scan.db "SELECT scan_id, status, processed_issues, total_issues FROM scans;"
```

## Current Behavior (Without CLI):

- ✅ Progress IS saved automatically
- ❌ Next run starts a NEW scan (doesn't resume)
- ✅ Old scan data remains in database
- ❌ No way to resume from CLI (must edit code manually)

## Workaround (Until CLI is Added):

Manually edit `jira_dc_scanner.py` line ~1450:

```python
# Change from:
results = scanner.scan()

# To:
results = scanner.scan(resume=True, scan_id='YOUR_SCAN_ID_HERE')
```
