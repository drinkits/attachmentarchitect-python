# 🏢 Jira Data Center Attachment Analysis Tool - Technical Design Document

## Executive Summary

This document outlines the technical design for a Python-based attachment analysis tool for **Jira Data Center (versions 9 and 10)**. The tool will provide comprehensive attachment analysis capabilities similar to the Forge Cloud version, but optimized for on-premise deployments.

**Target Environment**: Jira Data Center 9.x and 10.x (On-Premise)  
**Implementation**: Python 3.8+ standalone application  
**Key Requirement**: Must provide ALL information scopes about attachments with acceptable performance

---

## Table of Contents

1. [Technical Feasibility Analysis](#technical-feasibility-analysis)
2. [API Compatibility Assessment](#api-compatibility-assessment)
3. [Performance Strategy](#performance-strategy)
4. [Architecture Design](#architecture-design)
5. [Key Differences: Cloud vs Data Center](#key-differences-cloud-vs-data-center)
6. [Implementation Roadmap](#implementation-roadmap)
7. [Risk Mitigation](#risk-mitigation)

---

## Technical Feasibility Analysis

### ✅ Can It Be Done?

**YES - 100% Feasible**

#### API Access Verification

Jira Data Center provides robust REST API access:

| Capability | Endpoint | Available in DC 9/10 |
|------------|----------|---------------------|
| Search Issues | `GET /rest/api/2/search` | ✅ Yes |
| Get Issue Details | `GET /rest/api/2/issue/{issueKey}` | ✅ Yes |
| Get Attachments | Included in issue response | ✅ Yes |
| Download Attachment | `GET {attachment.content}` | ✅ Yes |
| Get Projects | `GET /rest/api/2/project` | ✅ Yes |
| Get Users | `GET /rest/api/2/user` | ✅ Yes |

#### Required Permissions

The API user needs:
- **Browse Projects** permission (minimum)
- **View Issues** permission
- **Admin access** (recommended for full-instance scans)

#### Authentication Methods

Jira Data Center supports:
1. **Basic Authentication** (username + password)
2. **Personal Access Tokens** (DC 8.14+) - **RECOMMENDED**
3. **OAuth 1.0a** (for app integrations)

**Conclusion**: No API blockers. All required data is accessible.

---

## API Compatibility Assessment

### Jira Data Center vs Cloud API Differences

| Feature | Cloud (v3) | Data Center (v2) | Impact |
|---------|-----------|------------------|--------|
| Base Path | `/rest/api/3/` | `/rest/api/2/` | Minor - just URL change |
| Search Endpoint | `/search/jql` | `/search` | Minor - parameter adjustment |
| Approximate Count | ✅ Available | ❌ Not available | Medium - need workaround |
| Pagination | `startAt`, `maxResults` | `startAt`, `maxResults` | None - identical |
| Attachment Fields | Same structure | Same structure | None |
| Rate Limiting | Strict (10 req/sec) | Configurable/Lenient | Positive - faster possible |

### Key API Adjustments Needed

#### 1. Issue Count Strategy

**Cloud Approach:**
```python
# Cloud has dedicated endpoint
POST /rest/api/3/search/approximate-count
```

**Data Center Approach:**
```python
# Must use search with maxResults=0 to get total
GET /rest/api/2/search?jql=...&maxResults=0
# Response includes: "total": 12543
```

#### 2. Search Endpoint

**Cloud:**
```python
POST /rest/api/3/search/jql
```

**Data Center:**
```python
GET /rest/api/2/search?jql=...&startAt=0&maxResults=100
# Or POST with body
```

#### 3. User Fields

**Cloud:** Uses `accountId` (GDPR-compliant)  
**Data Center:** Uses `name` and `key` fields (traditional usernames)

**Impact:** Need to handle both field structures

---

## Performance Strategy

### 🚀 Performance Analysis

#### The Critical Question: Will It Be "Drastiski Lēns" (Horribly Slow)?

**Answer: NO - If architected correctly**

### Performance Advantages in Data Center

#### 1. **LAN Speed Advantage** 🏆

**Massive Performance Win:**
- **Cloud**: Downloads traverse public internet (variable latency, bandwidth limits)
- **Data Center**: LAN speeds (1-10 Gbps typical)
- **Impact**: 10-100x faster file downloads

**Example:**
```
100 MB file download:
- Cloud (10 Mbps): ~80 seconds
- LAN (1 Gbps): ~0.8 seconds
```

#### 2. **Relaxed Rate Limiting**

- **Cloud**: Strict 10 requests/second limit
- **Data Center**: Configurable, often 100+ requests/second
- **Impact**: Can process batches much faster

#### 3. **Direct Database Access (Optional)**

For extreme performance, could query Jira database directly:
- **Pros**: Instant access to all data
- **Cons**: Requires DB credentials, version-specific schema knowledge
- **Recommendation**: Use API first, DB as optional "turbo mode"

### Performance Challenges

#### 1. **Single-Threaded Bottleneck**

**Problem:** Python script runs on one machine vs Cloud's distributed architecture

**Solution:** Multi-threaded/async processing

#### 2. **Large File Downloads**

**Problem:** Some attachments may be very large (GB+)

**Solution:** 
- Stream downloads (don't load entire file in memory)
- Hash calculation on-the-fly during download
- Skip files over configurable size threshold

#### 3. **Network Interruptions**

**Problem:** Long-running scans may be interrupted

**Solution:** Checkpoint/resume capability

---

## Architecture Design

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│           JIRA DATA CENTER ANALYSIS TOOL ARCHITECTURE           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    CLI Interface                          │  │
│  │  - Argument parsing                                       │  │
│  │  - Configuration loading                                  │  │
│  │  - Progress display (tqdm)                                │  │
│  └──────────────────────────────────────────────────────────┘  │
│                            │                                     │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Scan Orchestrator                            │  │
│  │  - Manages scan lifecycle                                 │  │
│  │  - Coordinates workers                                    │  │
│  │  - Handles checkpointing                                  │  │
│  └──────────────────────────────────────────────────────────┘  │
│           │                    │                    │            │
│  ┌────────▼────────┐  ┌───────▼────────┐  ┌───────▼────────┐  │
│  │  Issue Fetcher  │  │ Download Pool  │  │  Hash Engine   │  │
│  │  (API Client)   │  │ (ThreadPool)   │  │  (SHA-256)     │  │
│  │                 │  │                │  │                │  │
│  │ - Batch fetch   │  │ - 8-16 threads │  │ - Streaming    │  │
│  │ - Pagination    │  │ - Parallel DL  │  │ - Incremental  │  │
│  │ - Rate limit    │  │ - Queue mgmt   │  │ - Memory safe  │  │
│  └─────────────────┘  └────────────────┘  └────────────────┘  │
│                            │                                     │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Duplicate Detector                           │  │
│  │  - Hash comparison                                        │  │
│  │  - Group management                                       │  │
│  │  - Statistics aggregation                                 │  │
│  └──────────────────────────────────────────────────────────┘  │
│                            │                                     │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Storage Manager                              │  │
│  │  - SQLite database                                        │  │
│  │  - Checkpoint saves                                       │  │
│  │  - Resume capability                                      │  │
│  │  - Export formats (JSON, CSV, Excel)                      │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
└───────��─────────────────────────────────────────────────────────┘
```

### Core Components

#### 1. **Jira Data Center API Client**

```python
class JiraDataCenterClient:
    """
    API client optimized for Jira Data Center.
    
    Features:
    - Personal Access Token authentication
    - API v2 compatibility
    - Configurable rate limiting
    - Connection pooling
    - Retry logic with exponential backoff
    """
    
    def __init__(self, base_url, token, max_requests_per_second=50):
        self.base_url = base_url
        self.token = token
        self.rate_limiter = RateLimiter(max_requests_per_second)
        self.session = self._create_session()
    
    def search_issues(self, jql, start_at=0, max_results=100, fields=None):
        """Search issues using JQL with pagination."""
        pass
    
    def get_total_issue_count(self, jql):
        """Get total count using maxResults=0 trick."""
        pass
    
    def download_attachment(self, url, stream=True):
        """Download attachment with streaming support."""
        pass
```

#### 2. **Multi-Threaded Download Manager**

```python
from concurrent.futures import ThreadPoolExecutor, as_completed

class DownloadManager:
    """
    Manages parallel attachment downloads.
    
    This is THE performance game-changer.
    Uses thread pool to download multiple files simultaneously.
    """
    
    def __init__(self, jira_client, num_workers=12):
        self.jira_client = jira_client
        self.executor = ThreadPoolExecutor(max_workers=num_workers)
        self.active_downloads = 0
    
    def download_and_hash_batch(self, attachments):
        """
        Download and hash multiple attachments in parallel.
        
        Returns: List of (attachment_id, file_hash, metadata)
        """
        futures = []
        
        for attachment in attachments:
            future = self.executor.submit(
                self._download_and_hash_single,
                attachment
            )
            futures.append(future)
        
        results = []
        for future in as_completed(futures):
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                # Log error but continue
                logger.error(f"Download failed: {e}")
        
        return results
    
    def _download_and_hash_single(self, attachment):
        """Download single file and calculate hash."""
        # Stream download to avoid memory issues
        # Calculate hash incrementally
        pass
```

#### 3. **Streaming Hash Calculator**

```python
import hashlib

class StreamingHasher:
    """
    Calculate file hash without loading entire file in memory.
    Critical for large attachments.
    """
    
    @staticmethod
    def hash_from_stream(file_stream, chunk_size=8192):
        """
        Calculate SHA-256 hash from stream.
        
        Args:
            file_stream: File-like object (from requests.iter_content)
            chunk_size: Bytes to read per iteration
            
        Returns:
            str: Hexadecimal hash
        """
        hasher = hashlib.sha256()
        
        for chunk in file_stream:
            if chunk:  # Filter out keep-alive chunks
                hasher.update(chunk)
        
        return hasher.hexdigest()
```

#### 4. **Checkpoint Manager**

```python
class CheckpointManager:
    """
    Manages scan progress and resume capability.
    
    Critical for long-running scans that may be interrupted.
    """
    
    def __init__(self, db_path):
        self.db = sqlite3.connect(db_path)
        self.create_checkpoint_table()
    
    def save_checkpoint(self, scan_id, processed_issues, last_issue_key):
        """Save current progress."""
        pass
    
    def load_checkpoint(self, scan_id):
        """Load previous progress to resume scan."""
        pass
    
    def mark_attachment_processed(self, scan_id, attachment_id, file_hash):
        """Mark individual attachment as processed."""
        pass
    
    def get_processed_attachments(self, scan_id):
        """Get set of already-processed attachment IDs."""
        pass
```

#### 5. **Progress Reporter**

```python
from tqdm import tqdm

class ProgressReporter:
    """
    Provides real-time feedback to user.
    
    Essential for user confidence during long scans.
    """
    
    def __init__(self, total_issues):
        self.pbar = tqdm(
            total=total_issues,
            desc="Analyzing Issues",
            unit="issues",
            bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]'
        )
        self.stats = {
            'files_processed': 0,
            'duplicates_found': 0,
            'bytes_scanned': 0
        }
    
    def update(self, issues_processed=1, files=0, duplicates=0, bytes_size=0):
        """Update progress bar and statistics."""
        self.pbar.update(issues_processed)
        self.stats['files_processed'] += files
        self.stats['duplicates_found'] += duplicates
        self.stats['bytes_scanned'] += bytes_size
        
        # Update postfix with live stats
        self.pbar.set_postfix({
            'files': self.stats['files_processed'],
            'dupes': self.stats['duplicates_found'],
            'size': self._format_bytes(self.stats['bytes_scanned'])
        })
```

---

## Key Differences: Cloud vs Data Center

### Comparison Matrix

| Aspect | Cloud (Forge) | Data Center (Python) |
|--------|---------------|---------------------|
| **API Version** | REST API v3 | REST API v2 |
| **Authentication** | OAuth 2.0 (automatic) | Personal Access Token |
| **Execution Model** | Serverless (distributed) | Single-process (multi-threaded) |
| **Storage** | Forge Storage (240KB limit) | SQLite (unlimited) |
| **Rate Limiting** | 10 req/sec (strict) | Configurable (50-100+ req/sec) |
| **Network Speed** | Internet (variable) | LAN (1-10 Gbps) |
| **Deployment** | Cloud-hosted | On-premise script |
| **Scaling** | Automatic (parallel functions) | Manual (thread pool size) |
| **Cost** | Per-user licensing | One-time deployment |
| **Resume Capability** | Built-in (Forge Storage) | Custom (SQLite checkpoints) |

### Adaptation Strategy

#### 1. **API Endpoint Mapping**

```python
# Cloud → Data Center mapping
ENDPOINT_MAP = {
    'search': {
        'cloud': '/rest/api/3/search/jql',
        'dc': '/rest/api/2/search'
    },
    'issue': {
        'cloud': '/rest/api/3/issue/{key}',
        'dc': '/rest/api/2/issue/{key}'
    }
}
```

#### 2. **User Field Handling**

```python
def get_user_identifier(user_obj, is_cloud=False):
    """
    Extract user identifier based on platform.
    
    Cloud: Uses accountId (GDPR-compliant)
    DC: Uses name/key (traditional username)
    """
    if is_cloud:
        return user_obj.get('accountId')
    else:
        return user_obj.get('name') or user_obj.get('key')
```

#### 3. **Hash Strategy**

**Cloud Approach:** Hash the content URL (fast, no download)
```python
# Cloud: Hash URL as proxy for content
file_hash = hashlib.sha256(content_url.encode()).hexdigest()
```

**Data Center Approach:** Hash actual file content (accurate, slower but acceptable with LAN speeds)
```python
# DC: Hash actual file content for accuracy
response = jira_client.download_attachment(content_url, stream=True)
file_hash = StreamingHasher.hash_from_stream(response.iter_content(8192))
```

**Why the difference?**
- **Cloud**: Can't download files (too slow over internet, rate limits)
- **Data Center**: CAN download files (LAN speeds make it feasible)
- **Benefit**: More accurate duplicate detection (catches identical files with different URLs)

---

## Implementation Roadmap

### Phase 1: Core Scanning Engine (Week 1)

**Deliverables:**
- [ ] Jira DC API client with authentication
- [ ] Issue search with pagination
- [ ] Basic attachment metadata extraction
- [ ] SQLite storage setup
- [ ] Simple progress reporting

**Success Criteria:** Can scan 1,000 issues and store metadata

### Phase 2: Performance Optimization (Week 2)

**Deliverables:**
- [ ] Multi-threaded download manager
- [ ] Streaming hash calculator
- [ ] Rate limiter implementation
- [ ] Memory-efficient processing
- [ ] Performance benchmarking

**Success Criteria:** Can process 10,000 issues in under 30 minutes

### Phase 3: Duplicate Detection & Analysis (Week 3)

**Deliverables:**
- [ ] Hash-based duplicate detection
- [ ] Statistics aggregation (by project, user, type)
- [ ] Quick Wins calculation
- [ ] Age-based analysis
- [ ] Status-based analysis

**Success Criteria:** Produces complete analysis report

### Phase 4: Resilience & UX (Week 4)

**Deliverables:**
- [ ] Checkpoint/resume capability
- [ ] Error handling and retry logic
- [ ] Enhanced progress reporting (tqdm)
- [ ] Configuration file support
- [ ] Logging system

**Success Criteria:** Can resume interrupted scans

### Phase 5: Reporting & Export (Week 5)

**Deliverables:**
- [ ] JSON export
- [ ] CSV export
- [ ] Excel export with charts
- [ ] HTML report generation
- [ ] CLI summary output

**Success Criteria:** Generates professional reports

### Phase 6: Advanced Features (Week 6)

**Deliverables:**
- [ ] Project filtering
- [ ] Date range filtering
- [ ] File type filtering
- [ ] Size threshold configuration
- [ ] Dry-run mode
- [ ] Comparison mode (compare two scans)

**Success Criteria:** Full feature parity with Cloud version

---

## Risk Mitigation

### Risk Matrix

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **Slow performance** | Medium | High | Multi-threading, LAN deployment, streaming |
| **Memory exhaustion** | Medium | High | Streaming downloads, batch processing |
| **Network interruption** | Low | Medium | Checkpoint/resume, retry logic |
| **API rate limiting** | Low | Low | Configurable rate limiter |
| **Large file timeout** | Medium | Medium | Streaming, configurable timeout |
| **Permission issues** | Low | High | Clear documentation, permission checker |
| **Version compatibility** | Low | Medium | Test on DC 9 and 10, version detection |

### Performance Safeguards

#### 1. **Memory Management**

```python
# Never load entire file in memory
def download_with_streaming(url):
    response = requests.get(url, stream=True)
    # Process in chunks
    for chunk in response.iter_content(chunk_size=8192):
        process_chunk(chunk)
```

#### 2. **Timeout Configuration**

```python
# Prevent hanging on large files
DOWNLOAD_TIMEOUT = 300  # 5 minutes max per file
response = requests.get(url, timeout=DOWNLOAD_TIMEOUT, stream=True)
```

#### 3. **Size Limits**

```python
# Skip extremely large files
MAX_FILE_SIZE = 5 * 1024 * 1024 * 1024  # 5 GB
if attachment['size'] > MAX_FILE_SIZE:
    logger.warning(f"Skipping large file: {attachment['filename']}")
    continue
```

#### 4. **Graceful Degradation**

```python
# If download fails, fall back to URL-based hashing
try:
    file_hash = hash_file_content(attachment_url)
except DownloadError:
    logger.warning("Download failed, using URL hash")
    file_hash = hash_url(attachment_url)
```

---

## Performance Projections

### Estimated Scan Times

**Assumptions:**
- LAN connection: 1 Gbps
- Thread pool: 12 workers
- Average file size: 2 MB
- API rate: 50 requests/second

| Instance Size | Issues | Attachments | Estimated Time | Throughput |
|--------------|--------|-------------|----------------|------------|
| **Small** | 1,000 | 500 | 2-3 minutes | 333 issues/min |
| **Medium** | 10,000 | 5,000 | 15-20 minutes | 500 issues/min |
| **Large** | 100,000 | 50,000 | 2-3 hours | 555 issues/min |
| **Enterprise** | 500,000 | 250,000 | 10-15 hours | 555 issues/min |

**Comparison to Cloud:**
- Small instances: Similar speed
- Medium instances: 2-3x slower (but still acceptable)
- Large instances: 5-10x slower (but runs overnight)

**Verdict:** Performance is acceptable for a pre-migration audit tool.

---

## Technical Specifications

### System Requirements

**Minimum:**
- Python 3.8+
- 4 GB RAM
- 10 GB free disk space
- Network access to Jira DC server

**Recommended:**
- Python 3.10+
- 16 GB RAM
- 50 GB free disk space (for large instances)
- Server on same LAN as Jira DC
- SSD storage

### Dependencies

```
requests>=2.31.0          # HTTP client
tqdm>=4.66.0              # Progress bars
python-dotenv>=1.0.0      # Configuration
openpyxl>=3.1.0           # Excel export
pandas>=2.0.0             # Data analysis
jinja2>=3.1.0             # HTML reports
```

### Configuration File

```yaml
# config.yaml
jira:
  base_url: "https://jira.company.com"
  token: "${JIRA_TOKEN}"  # From environment variable
  verify_ssl: true

scan:
  batch_size: 100
  thread_pool_size: 12
  max_file_size_gb: 5
  download_timeout_seconds: 300
  rate_limit_per_second: 50

storage:
  database_path: "./scans/scan.db"
  checkpoint_interval: 100  # Save every N issues

output:
  formats: ["json", "csv", "excel", "html"]
  output_dir: "./reports"

filters:
  projects: []  # Empty = all projects
  date_from: null
  date_to: null
  file_types: []  # Empty = all types
```

---

## Conclusion

### ✅ Feasibility: CONFIRMED

The Jira Data Center attachment analysis tool is **100% technically feasible** with excellent performance characteristics when properly architected.

### 🚀 Performance: ACCEPTABLE

With multi-threaded downloads and LAN deployment, performance will be:
- **Fast enough** for practical use
- **Not "drastiski lēns"** (horribly slow)
- **Suitable** for pre-migration audits and periodic analysis

### 🎯 Key Success Factors

1. **Multi-threading** - The game-changer for performance
2. **Streaming downloads** - Prevents memory issues
3. **Checkpoint/resume** - Handles interruptions gracefully
4. **LAN deployment** - Leverages network speed advantage
5. **Clear progress feedback** - Builds user confidence

### 📋 Next Steps

1. **Review and approve** this design document
2. **Set up development environment**
3. **Begin Phase 1 implementation** (Core Scanning Engine)
4. **Test on small Jira DC instance** (1,000 issues)
5. **Optimize and iterate** based on real-world performance

---

**Document Version:** 1.0  
**Date:** January 2025  
**Status:** Ready for Implementation  
**Estimated Development Time:** 6 weeks to full feature parity
