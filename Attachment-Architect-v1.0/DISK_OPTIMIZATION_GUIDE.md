# Disk I/O Optimization Guide

## Problem
Running scans causes high disk usage and makes your PC hot due to:
1. **Frequent checkpoint saves** (every 100 issues by default)
2. **SQLite writes** to disk for every batch
3. **No in-memory buffering**

## Quick Fix: Reduce Disk Writes

### Option 1: Increase Checkpoint Interval (Recommended)

Edit `config.yaml` and change:

```yaml
storage:
  database_path: "./scans/scan.db"
  checkpoint_interval: 500  # Changed from 100 to 500
```

**Benefits:**
- ✅ 5x fewer disk writes
- ✅ Faster scanning
- ✅ Less heat generation
- ⚠️ If scan is interrupted, you lose progress of last 500 issues (not critical)

### Option 2: Use RAM Disk (Advanced)

**Windows:**
1. Download ImDisk Toolkit (free)
2. Create a RAM disk (e.g., R: drive with 2GB)
3. Edit `config.yaml`:

```yaml
storage:
  database_path: "R:/scans/scan.db"  # Use RAM disk
  checkpoint_interval: 1000  # Even less frequent saves
```

**Benefits:**
- ✅ 10-100x faster disk operations
- ✅ Minimal heat generation
- ✅ Much faster scanning
- ⚠️ Data lost if PC crashes (but scan can resume)

### Option 3: Disable Content Hashing (Fastest)

Edit `config.yaml`:

```yaml
scan:
  use_content_hash: false  # Use URL-based hashing instead
  thread_pool_size: 6      # Reduce threads to lower CPU/disk load
```

**Benefits:**
- ✅ No file downloads = no disk writes
- ✅ Much faster (10x+)
- ✅ Minimal heat
- ⚠️ Less accurate duplicate detection (URL-based instead of content-based)

## Recommended Settings for Hot PC

```yaml
# config.yaml - Optimized for low disk I/O

jira:
  base_url: ${JIRA_BASE_URL}
  verify_ssl: true

scan:
  batch_size: 100
  thread_pool_size: 6              # Reduced from 12
  max_file_size_gb: 5
  download_timeout_seconds: 300
  rate_limit_per_second: 30        # Reduced from 50
  use_content_hash: true           # Keep true for accuracy

storage:
  database_path: "./scans/scan.db"
  checkpoint_interval: 500         # Increased from 100

output:
  output_dir: "./reports"

filters:
  projects: []
  date_from: null
  date_to: null
  custom_jql: null

logging:
  level: "INFO"
  file: "./logs/scanner.log"
  console: true
```

## Performance Comparison

| Setting | Disk Writes | Speed | Heat | Accuracy |
|---------|-------------|-------|------|----------|
| **Default** (checkpoint=100) | High | Medium | High | 100% |
| **Optimized** (checkpoint=500) | Low | Fast | Low | 100% |
| **RAM Disk** (checkpoint=1000) | Minimal | Very Fast | Minimal | 100% |
| **URL Hash** (no downloads) | Minimal | Ultra Fast | Minimal | 95% |

## Apply Changes

1. **Edit config.yaml** with your preferred settings
2. **Restart the scan**:
   ```bash
   run_scan.bat
   ```

3. **Monitor improvement**:
   - Check Task Manager → Performance → Disk
   - Should see much lower disk usage
   - PC should stay cooler

## Additional Tips

### 1. Close Other Programs
- Close browsers, IDEs, etc. during scan
- Reduces overall disk contention

### 2. Use SSD (if available)
- SSDs handle random writes better than HDDs
- Less heat generation

### 3. Scan During Off-Hours
- Run overnight when PC can cool down
- Less competition for resources

### 4. Monitor Temperature
- Use HWMonitor or similar tool
- If temp >80°C, reduce `thread_pool_size` further

## Troubleshooting

### PC Still Hot?
1. Reduce `thread_pool_size` to 4
2. Increase `checkpoint_interval` to 1000
3. Consider `use_content_hash: false`

### Scan Too Slow?
1. Increase `thread_pool_size` to 8
2. Decrease `checkpoint_interval` to 250
3. Use RAM disk

### Want Balance?
```yaml
thread_pool_size: 6
checkpoint_interval: 500
use_content_hash: true
```

This gives good speed with minimal heat! 🎯
