# 🐍 Attachment Architect: Python Scanning Port Guide

## Executive Summary

This document provides a comprehensive guide for porting the Attachment Architect scanning capability from Atlassian Forge (Node.js) to a standalone Python application. The scanning engine analyzes Jira Cloud instances to identify duplicate attachments and storage waste patterns.

**Original Implementation**: Atlassian Forge serverless app (Node.js 22.x)  
**Target Implementation**: Python 3.8+ standalone application  
**Performance**: ~25x faster than traditional methods (processes 10,000 issues in ~5 minutes)

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Core Scanning Algorithm](#core-scanning-algorithm)
3. [Data Structures](#data-structures)
4. [API Integration](#api-integration)
5. [Storage Strategy](#storage-strategy)
6. [Python Implementation Guide](#python-implementation-guide)
7. [Performance Optimization](#performance-optimization)
8. [Error Handling](#error-handling)
9. [Testing Strategy](#testing-strategy)
10. [Deployment Considerations](#deployment-considerations)

---

## Architecture Overview

### High-Level Flow

```
┌─────────────────────────────────────────────────────────────┐
│                    SCANNING ARCHITECTURE                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. Initialize Scan                                         │
│     ├─ Generate scan ID                                     │
│     ├─ Get total issue count (approximate)                  │
│     └─ Initialize storage structures                        │
│                                                              │
│  2. Batch Processing Loop                                   │
│     ├─ Fetch 250 issues per batch (with attachments)        │
│     ├─ Process each attachment:                             │
│     │  ├─ Calculate hash (SHA-256 from URL)                 │
│     │  ├─ Check if duplicate                                │
│     │  ├─ Update statistics                                 │
│     │  └─ Store metadata                                    │
│     ├─ Save progress                                        │
│     └─ Repeat until all issues processed                    │
│                                                              │
│  3. Finalize Scan                                           │
│     ├─ Calculate final statistics                           │
│     ├─ Generate insights (Quick Wins, etc.)                 │
│     └─ Save results                                         │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Key Components

1. **Jira API Client**: Handles authentication and API requests
2. **Batch Processor**: Fetches and processes issues in batches
3. **Duplicate Detector**: Identifies duplicate files using SHA-256 hashing
4. **Statistics Aggregator**: Calculates storage metrics by project, user, file type, etc.
5. **Storage Manager**: Persists scan data and results
6. **Progress Tracker**: Reports real-time progress

---

## Core Scanning Algorithm

### Main Scanning Loop

```python
def scan_jira_instance(jira_client, storage_manager):
    """
    Main scanning function that orchestrates the entire process.
    
    Args:
        jira_client: Authenticated Jira API client
        storage_manager: Handles data persistence
        
    Returns:
        dict: Scan results with statistics and insights
    """
    # 1. Initialize scan
    scan_id = generate_scan_id()
    total_issues = get_approximate_issue_count(jira_client)
    
    scan_state = {
        'scan_id': scan_id,
        'status': 'running',
        'total_issues': total_issues,
        'processed_issues': 0,
        'start_time': datetime.utcnow().isoformat()
    }
    
    # Initialize data structures
    duplicate_groups = {}  # Hash -> file metadata
    scan_stats = initialize_stats()
    
    # 2. Process in batches
    batch_size = 250
    start_at = 0
    
    while start_at < total_issues:
        # Fetch batch of issues
        issues = fetch_issues_batch(
            jira_client, 
            start_at=start_at, 
            max_results=batch_size
        )
        
        if not issues:
            break
            
        # Process each issue
        for issue in issues:
            process_issue(
                issue, 
                duplicate_groups, 
                scan_stats, 
                scan_id
            )
            
        # Update progress
        scan_state['processed_issues'] += len(issues)
        storage_manager.save_progress(scan_state, scan_stats, duplicate_groups)
        
        # Move to next batch
        start_at += batch_size
        
        # Rate limiting (optional delay)
        time.sleep(0.05)  # 50ms delay
    
    # 3. Finalize scan
    scan_state['status'] = 'completed'
    scan_state['completion_time'] = datetime.utcnow().isoformat()
    
    # Calculate insights
    quick_wins = calculate_quick_wins(duplicate_groups)
    user_stats = calculate_user_stats(duplicate_groups)
    age_stats = calculate_age_stats(duplicate_groups)
    status_stats = calculate_status_stats(duplicate_groups)
    
    # Save final results
    results = {
        'scan_state': scan_state,
        'scan_stats': scan_stats,
        'duplicate_groups': duplicate_groups,
        'quick_wins': quick_wins,
        'user_stats': user_stats,
        'age_stats': age_stats,
        'status_stats': status_stats
    }
    
    storage_manager.save_final_results(results)
    
    return results
```

### Issue Processing

```python
def process_issue(issue, duplicate_groups, scan_stats, scan_id):
    """
    Process a single issue and its attachments.
    
    Args:
        issue: Jira issue object
        duplicate_groups: Dictionary tracking duplicate files
        scan_stats: Statistics accumulator
        scan_id: Current scan identifier
    """
    issue_key = issue['key']
    project_key = issue['fields']['project']['key']
    project_name = issue['fields']['project']['name']
    
    # Extract status information
    status = issue['fields']['status']['name']
    status_category = issue['fields']['status']['statusCategory']['name']
    status_category_key = issue['fields']['status']['statusCategory']['key']
    
    # Get issue last updated timestamp
    issue_last_updated = issue['fields']['updated']
    
    # Process attachments
    attachments = issue['fields'].get('attachment', [])
    
    for attachment in attachments:
        process_attachment(
            attachment,
            issue_key,
            project_key,
            project_name,
            status,
            status_category,
            status_category_key,
            issue_last_updated,
            duplicate_groups,
            scan_stats,
            scan_id
        )
```

### Attachment Processing

```python
def process_attachment(attachment, issue_key, project_key, project_name,
                      status, status_category, status_category_key,
                      issue_last_updated, duplicate_groups, scan_stats, scan_id):
    """
    Process a single attachment and update statistics.
    
    Args:
        attachment: Jira attachment object
        issue_key: Issue key (e.g., "PROJ-123")
        project_key: Project key (e.g., "PROJ")
        project_name: Project display name
        status: Issue status name
        status_category: Status category name (To Do, In Progress, Done)
        status_category_key: Status category key (new, indeterminate, done)
        issue_last_updated: ISO timestamp of last issue update
        duplicate_groups: Dictionary tracking duplicates
        scan_stats: Statistics accumulator
        scan_id: Current scan identifier
    """
    # Extract attachment metadata
    attachment_id = attachment['id']
    file_name = attachment['filename']
    file_size = attachment['size']
    mime_type = attachment['mimeType']
    content_url = attachment['content']
    created = attachment['created']
    author = attachment['author']['displayName']
    author_id = attachment['author']['accountId']
    
    # Calculate hash from content URL
    # In Forge, we use crypto.createHash('sha256').update(contentUrl).digest('hex')
    # In Python, we use hashlib
    file_hash = calculate_hash(content_url)
    
    # Extract file extension
    file_extension = get_file_extension(file_name)
    
    # Check if this is a duplicate
    if file_hash in duplicate_groups:
        # DUPLICATE FILE
        group = duplicate_groups[file_hash]
        group['duplicate_count'] += 1
        group['total_wasted_space'] += file_size
        
        # Store location (limit to 20 locations per file)
        if len(group['locations']) < 20:
            group['locations'].append({
                'issue_key': issue_key,
                'project_key': project_key,
                'attachment_id': attachment_id,
                'is_canonical': False,
                'date_added': created,
                'author': author
            })
        
        # Update statistics
        scan_stats['duplicate_files'] += 1
        scan_stats['duplicate_size'] += file_size
        
    else:
        # CANONICAL FILE (first occurrence)
        duplicate_groups[file_hash] = {
            'file_name': file_name,
            'file_size': file_size,
            'mime_type': mime_type,
            'canonical_issue_key': issue_key,
            'canonical_attachment_id': attachment_id,
            'duplicate_count': 0,
            'total_wasted_space': 0,
            'author': author,
            'author_id': author_id,
            'created': created,
            'status': status,
            'status_category': status_category,
            'status_category_key': status_category_key,
            'issue_last_updated': issue_last_updated,
            'locations': [{
                'issue_key': issue_key,
                'project_key': project_key,
                'attachment_id': attachment_id,
                'is_canonical': True,
                'date_added': created,
                'author': author
            }]
        }
        
        # Update statistics
        scan_stats['canonical_files'] += 1
    
    # Update global statistics
    scan_stats['total_files'] += 1
    scan_stats['total_size'] += file_size
    scan_stats['processed_issues'] = scan_stats.get('processed_issues', 0) + 1
    
    # Update per-project statistics
    if project_key not in scan_stats['project_stats']:
        scan_stats['project_stats'][project_key] = {
            'project_name': project_name,
            'total_size': 0,
            'duplicate_size': 0,
            'file_count': 0,
            'duplicate_count': 0
        }
    
    project_stats = scan_stats['project_stats'][project_key]
    project_stats['total_size'] += file_size
    project_stats['file_count'] += 1
    
    if file_hash in duplicate_groups and duplicate_groups[file_hash]['duplicate_count'] > 0:
        project_stats['duplicate_size'] += file_size
        project_stats['duplicate_count'] += 1
    
    # Update per-file-type statistics
    if file_extension not in scan_stats['file_type_stats']:
        scan_stats['file_type_stats'][file_extension] = {
            'total_size': 0,
            'count': 0
        }
    
    file_type_stats = scan_stats['file_type_stats'][file_extension]
    file_type_stats['total_size'] += file_size
    file_type_stats['count'] += 1
```

### Hash Calculation

```python
import hashlib

def calculate_hash(content_url):
    """
    Calculate SHA-256 hash from content URL.
    
    In the original Forge implementation, we hash the content URL
    as a proxy for file content. This is fast and doesn't require
    downloading the file.
    
    Args:
        content_url: Jira attachment content URL
        
    Returns:
        str: Hexadecimal SHA-256 hash
    """
    return hashlib.sha256(content_url.encode('utf-8')).hexdigest()
```

---

## Data Structures

### Scan State

```python
scan_state = {
    'scan_id': 'abc123xyz',           # Unique scan identifier
    'status': 'running',              # running | completed | failed
    'total_issues': 12543,            # Total issues to process
    'processed_issues': 5644,         # Issues processed so far
    'start_time': '2025-01-16T10:00:00Z',
    'completion_time': None,          # Set when scan completes
    'duration_ms': None               # Total scan duration
}
```

### Scan Statistics

```python
scan_stats = {
    'total_files': 15234,             # Total attachments found
    'total_size': 1567890123,         # Total storage in bytes
    'canonical_files': 12456,         # Unique files
    'duplicate_files': 2778,          # Duplicate files
    'duplicate_size': 345678901,      # Wasted storage in bytes
    'processed_issues': 12543,        # Issues scanned
    
    # Per-project breakdown
    'project_stats': {
        'PROJ': {
            'project_name': 'My Project',
            'total_size': 123456789,
            'duplicate_size': 23456789,
            'file_count': 1234,
            'duplicate_count': 234
        }
    },
    
    # Per-file-type breakdown
    'file_type_stats': {
        'pdf': {
            'total_size': 456789012,
            'count': 3456
        },
        'png': {
            'total_size': 234567890,
            'count': 5678
        }
    }
}
```

### Duplicate Groups

```python
duplicate_groups = {
    'a3f5b9c2...': {  # SHA-256 hash
        'file_name': 'report.pdf',
        'file_size': 1258291,
        'mime_type': 'application/pdf',
        'canonical_issue_key': 'PROJ-123',
        'canonical_attachment_id': '12345',
        'duplicate_count': 3,
        'total_wasted_space': 3774873,  # file_size * duplicate_count
        'author': 'John Doe',
        'author_id': 'account-id-123',
        'created': '2024-01-15T10:30:00Z',
        'status': 'In Progress',
        'status_category': 'In Progress',
        'status_category_key': 'indeterminate',
        'issue_last_updated': '2024-12-20T15:45:00Z',
        'locations': [
            {
                'issue_key': 'PROJ-123',
                'project_key': 'PROJ',
                'attachment_id': '12345',
                'is_canonical': True,
                'date_added': '2024-01-15T10:30:00Z',
                'author': 'John Doe'
            },
            {
                'issue_key': 'PROJ-456',
                'project_key': 'PROJ',
                'attachment_id': '67890',
                'is_canonical': False,
                'date_added': '2024-02-20T14:15:00Z',
                'author': 'Jane Smith'
            }
        ]
    }
}
```

---

## API Integration

### Jira Cloud REST API v3

The scanner uses the following Jira REST API endpoints:

#### 1. Get Approximate Issue Count

```python
def get_approximate_issue_count(jira_client):
    """
    Get approximate count of issues in the instance.
    
    Endpoint: POST /rest/api/3/search/approximate-count
    """
    url = f"{jira_client.base_url}/rest/api/3/search/approximate-count"
    
    payload = {
        "jql": "created >= -7300d ORDER BY created DESC"  # Last 20 years
    }
    
    response = jira_client.post(url, json=payload)
    response.raise_for_status()
    
    data = response.json()
    return data.get('count', 0)
```

#### 2. Fetch Issues with Attachments

```python
def fetch_issues_batch(jira_client, start_at=0, max_results=250):
    """
    Fetch a batch of issues with attachment data.
    
    Endpoint: POST /rest/api/3/search/jql
    """
    url = f"{jira_client.base_url}/rest/api/3/search/jql"
    
    payload = {
        "jql": "created >= -7300d ORDER BY created DESC",
        "startAt": start_at,
        "maxResults": max_results,
        "fields": [
            "key",
            "attachment",
            "project",
            "status",
            "updated"
        ]
    }
    
    response = jira_client.post(url, json=payload)
    response.raise_for_status()
    
    data = response.json()
    return data.get('issues', [])
```

### Authentication

The Python implementation should support multiple authentication methods:

#### Option 1: API Token (Recommended)

```python
import requests
from requests.auth import HTTPBasicAuth

class JiraClient:
    def __init__(self, base_url, email, api_token):
        self.base_url = base_url.rstrip('/')
        self.auth = HTTPBasicAuth(email, api_token)
        self.session = requests.Session()
        self.session.auth = self.auth
        self.session.headers.update({
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
    
    def get(self, url, **kwargs):
        return self.session.get(url, **kwargs)
    
    def post(self, url, **kwargs):
        return self.session.post(url, **kwargs)
```

#### Option 2: OAuth 2.0

```python
from requests_oauthlib import OAuth2Session

class JiraOAuthClient:
    def __init__(self, base_url, client_id, client_secret, token):
        self.base_url = base_url.rstrip('/')
        self.session = OAuth2Session(
            client_id=client_id,
            token=token
        )
        self.session.headers.update({
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
```

### Rate Limiting

Jira Cloud has rate limits (~10 requests/second per user). Implement rate limiting:

```python
import time
from datetime import datetime, timedelta

class RateLimiter:
    def __init__(self, max_requests=10, time_window=1.0):
        """
        Args:
            max_requests: Maximum requests allowed in time window
            time_window: Time window in seconds
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = []
    
    def wait_if_needed(self):
        """Wait if rate limit would be exceeded."""
        now = datetime.now()
        
        # Remove old requests outside time window
        cutoff = now - timedelta(seconds=self.time_window)
        self.requests = [req for req in self.requests if req > cutoff]
        
        # Check if we need to wait
        if len(self.requests) >= self.max_requests:
            oldest = self.requests[0]
            wait_time = (oldest + timedelta(seconds=self.time_window) - now).total_seconds()
            if wait_time > 0:
                time.sleep(wait_time)
        
        # Record this request
        self.requests.append(now)
```

---

## Storage Strategy

### Storage Options

#### Option 1: SQLite Database (Recommended for Standalone)

```python
import sqlite3
import json

class SQLiteStorage:
    def __init__(self, db_path='attachment_architect.db'):
        self.conn = sqlite3.connect(db_path)
        self.create_tables()
    
    def create_tables(self):
        """Create database schema."""
        cursor = self.conn.cursor()
        
        # Scan state table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scans (
                scan_id TEXT PRIMARY KEY,
                status TEXT,
                total_issues INTEGER,
                processed_issues INTEGER,
                start_time TEXT,
                completion_time TEXT,
                duration_ms INTEGER
            )
        ''')
        
        # Scan statistics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scan_stats (
                scan_id TEXT PRIMARY KEY,
                stats_json TEXT,
                FOREIGN KEY (scan_id) REFERENCES scans(scan_id)
            )
        ''')
        
        # Duplicate groups table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS duplicate_groups (
                scan_id TEXT,
                file_hash TEXT,
                group_json TEXT,
                PRIMARY KEY (scan_id, file_hash),
                FOREIGN KEY (scan_id) REFERENCES scans(scan_id)
            )
        ''')
        
        self.conn.commit()
    
    def save_progress(self, scan_state, scan_stats, duplicate_groups):
        """Save current scan progress."""
        cursor = self.conn.cursor()
        
        # Update scan state
        cursor.execute('''
            INSERT OR REPLACE INTO scans 
            (scan_id, status, total_issues, processed_issues, start_time)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            scan_state['scan_id'],
            scan_state['status'],
            scan_state['total_issues'],
            scan_state['processed_issues'],
            scan_state['start_time']
        ))
        
        # Save scan stats
        cursor.execute('''
            INSERT OR REPLACE INTO scan_stats (scan_id, stats_json)
            VALUES (?, ?)
        ''', (scan_state['scan_id'], json.dumps(scan_stats)))
        
        # Save duplicate groups (batch insert)
        for file_hash, group in duplicate_groups.items():
            cursor.execute('''
                INSERT OR REPLACE INTO duplicate_groups 
                (scan_id, file_hash, group_json)
                VALUES (?, ?, ?)
            ''', (scan_state['scan_id'], file_hash, json.dumps(group)))
        
        self.conn.commit()
```

#### Option 2: JSON Files

```python
import json
import os

class JSONStorage:
    def __init__(self, storage_dir='./scan_data'):
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)
    
    def save_progress(self, scan_state, scan_stats, duplicate_groups):
        """Save current scan progress to JSON files."""
        scan_id = scan_state['scan_id']
        
        # Save scan state
        with open(f'{self.storage_dir}/{scan_id}_state.json', 'w') as f:
            json.dump(scan_state, f, indent=2)
        
        # Save scan stats
        with open(f'{self.storage_dir}/{scan_id}_stats.json', 'w') as f:
            json.dump(scan_stats, f, indent=2)
        
        # Save duplicate groups
        with open(f'{self.storage_dir}/{scan_id}_duplicates.json', 'w') as f:
            json.dump(duplicate_groups, f, indent=2)
```

#### Option 3: PostgreSQL/MySQL (For Multi-User Deployments)

```python
import psycopg2
import json

class PostgreSQLStorage:
    def __init__(self, connection_string):
        self.conn = psycopg2.connect(connection_string)
        self.create_tables()
    
    def create_tables(self):
        """Create database schema."""
        cursor = self.conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scans (
                scan_id VARCHAR(255) PRIMARY KEY,
                status VARCHAR(50),
                total_issues INTEGER,
                processed_issues INTEGER,
                start_time TIMESTAMP,
                completion_time TIMESTAMP,
                duration_ms INTEGER
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scan_stats (
                scan_id VARCHAR(255) PRIMARY KEY,
                stats_json JSONB,
                FOREIGN KEY (scan_id) REFERENCES scans(scan_id)
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS duplicate_groups (
                scan_id VARCHAR(255),
                file_hash VARCHAR(64),
                group_json JSONB,
                PRIMARY KEY (scan_id, file_hash),
                FOREIGN KEY (scan_id) REFERENCES scans(scan_id)
            )
        ''')
        
        self.conn.commit()
```

---

## Python Implementation Guide

### Complete Example Implementation

```python
#!/usr/bin/env python3
"""
Attachment Architect - Python Scanner
Analyzes Jira Cloud instances for duplicate attachments and storage waste.
"""

import hashlib
import time
import json
import sqlite3
from datetime import datetime
from typing import Dict, List, Optional
import requests
from requests.auth import HTTPBasicAuth


class JiraClient:
    """Handles Jira API authentication and requests."""
    
    def __init__(self, base_url: str, email: str, api_token: str):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.auth = HTTPBasicAuth(email, api_token)
        self.session.headers.update({
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
    
    def get(self, endpoint: str, **kwargs):
        """Make GET request to Jira API."""
        url = f"{self.base_url}{endpoint}"
        response = self.session.get(url, **kwargs)
        response.raise_for_status()
        return response.json()
    
    def post(self, endpoint: str, **kwargs):
        """Make POST request to Jira API."""
        url = f"{self.base_url}{endpoint}"
        response = self.session.post(url, **kwargs)
        response.raise_for_status()
        return response.json()


class StorageManager:
    """Manages scan data persistence using SQLite."""
    
    def __init__(self, db_path: str = 'attachment_architect.db'):
        self.conn = sqlite3.connect(db_path)
        self.create_tables()
    
    def create_tables(self):
        """Create database schema."""
        cursor = self.conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scans (
                scan_id TEXT PRIMARY KEY,
                status TEXT,
                total_issues INTEGER,
                processed_issues INTEGER,
                start_time TEXT,
                completion_time TEXT,
                duration_ms INTEGER
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scan_stats (
                scan_id TEXT PRIMARY KEY,
                stats_json TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS duplicate_groups (
                scan_id TEXT,
                file_hash TEXT,
                group_json TEXT,
                PRIMARY KEY (scan_id, file_hash)
            )
        ''')
        
        self.conn.commit()
    
    def save_progress(self, scan_state: dict, scan_stats: dict, duplicate_groups: dict):
        """Save current scan progress."""
        cursor = self.conn.cursor()
        
        # Update scan state
        cursor.execute('''
            INSERT OR REPLACE INTO scans 
            (scan_id, status, total_issues, processed_issues, start_time)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            scan_state['scan_id'],
            scan_state['status'],
            scan_state['total_issues'],
            scan_state['processed_issues'],
            scan_state['start_time']
        ))
        
        # Save scan stats
        cursor.execute('''
            INSERT OR REPLACE INTO scan_stats (scan_id, stats_json)
            VALUES (?, ?)
        ''', (scan_state['scan_id'], json.dumps(scan_stats)))
        
        # Save duplicate groups
        for file_hash, group in duplicate_groups.items():
            cursor.execute('''
                INSERT OR REPLACE INTO duplicate_groups 
                (scan_id, file_hash, group_json)
                VALUES (?, ?, ?)
            ''', (scan_state['scan_id'], file_hash, json.dumps(group)))
        
        self.conn.commit()
    
    def save_final_results(self, results: dict):
        """Save final scan results."""
        scan_state = results['scan_state']
        cursor = self.conn.cursor()
        
        cursor.execute('''
            UPDATE scans 
            SET status = ?, completion_time = ?, duration_ms = ?
            WHERE scan_id = ?
        ''', (
            scan_state['status'],
            scan_state.get('completion_time'),
            scan_state.get('duration_ms'),
            scan_state['scan_id']
        ))
        
        self.conn.commit()


class AttachmentScanner:
    """Main scanner class that orchestrates the scanning process."""
    
    def __init__(self, jira_client: JiraClient, storage_manager: StorageManager):
        self.jira = jira_client
        self.storage = storage_manager
        self.batch_size = 250
    
    def scan(self) -> dict:
        """Execute full scan of Jira instance."""
        # 1. Initialize scan
        scan_id = self.generate_scan_id()
        total_issues = self.get_approximate_issue_count()
        
        scan_state = {
            'scan_id': scan_id,
            'status': 'running',
            'total_issues': total_issues,
            'processed_issues': 0,
            'start_time': datetime.utcnow().isoformat()
        }
        
        duplicate_groups = {}
        scan_stats = self.initialize_stats()
        
        print(f"Starting scan {scan_id}")
        print(f"Total issues to process: {total_issues}")
        
        # 2. Process in batches
        start_at = 0
        
        while start_at < total_issues:
            print(f"Processing batch starting at {start_at}...")
            
            # Fetch batch
            issues = self.fetch_issues_batch(start_at, self.batch_size)
            
            if not issues:
                break
            
            # Process each issue
            for issue in issues:
                self.process_issue(
                    issue,
                    duplicate_groups,
                    scan_stats,
                    scan_id
                )
            
            # Update progress
            scan_state['processed_issues'] += len(issues)
            progress_pct = (scan_state['processed_issues'] / total_issues) * 100
            print(f"Progress: {progress_pct:.1f}% ({scan_state['processed_issues']}/{total_issues})")
            
            # Save progress
            self.storage.save_progress(scan_state, scan_stats, duplicate_groups)
            
            # Move to next batch
            start_at += self.batch_size
            
            # Rate limiting
            time.sleep(0.05)
        
        # 3. Finalize scan
        end_time = datetime.utcnow()
        start_time = datetime.fromisoformat(scan_state['start_time'])
        duration_ms = int((end_time - start_time).total_seconds() * 1000)
        
        scan_state['status'] = 'completed'
        scan_state['completion_time'] = end_time.isoformat()
        scan_state['duration_ms'] = duration_ms
        
        # Calculate insights
        quick_wins = self.calculate_quick_wins(duplicate_groups)
        
        results = {
            'scan_state': scan_state,
            'scan_stats': scan_stats,
            'duplicate_groups': duplicate_groups,
            'quick_wins': quick_wins
        }
        
        self.storage.save_final_results(results)
        
        print(f"\nScan completed in {duration_ms/1000:.1f} seconds")
        print(f"Total files: {scan_stats['total_files']}")
        print(f"Duplicate files: {scan_stats['duplicate_files']}")
        print(f"Wasted storage: {self.format_bytes(scan_stats['duplicate_size'])}")
        
        return results
    
    def generate_scan_id(self) -> str:
        """Generate unique scan identifier."""
        import uuid
        return str(uuid.uuid4())[:8]
    
    def get_approximate_issue_count(self) -> int:
        """Get approximate count of issues."""
        data = self.jira.post('/rest/api/3/search/approximate-count', json={
            'jql': 'created >= -7300d ORDER BY created DESC'
        })
        return data.get('count', 0)
    
    def fetch_issues_batch(self, start_at: int, max_results: int) -> List[dict]:
        """Fetch batch of issues with attachments."""
        data = self.jira.post('/rest/api/3/search/jql', json={
            'jql': 'created >= -7300d ORDER BY created DESC',
            'startAt': start_at,
            'maxResults': max_results,
            'fields': ['key', 'attachment', 'project', 'status', 'updated']
        })
        return data.get('issues', [])
    
    def initialize_stats(self) -> dict:
        """Initialize statistics structure."""
        return {
            'total_files': 0,
            'total_size': 0,
            'canonical_files': 0,
            'duplicate_files': 0,
            'duplicate_size': 0,
            'processed_issues': 0,
            'project_stats': {},
            'file_type_stats': {}
        }
    
    def process_issue(self, issue: dict, duplicate_groups: dict, 
                     scan_stats: dict, scan_id: str):
        """Process a single issue and its attachments."""
        issue_key = issue['key']
        project = issue['fields']['project']
        project_key = project['key']
        project_name = project['name']
        
        status = issue['fields']['status']['name']
        status_category = issue['fields']['status']['statusCategory']['name']
        status_category_key = issue['fields']['status']['statusCategory']['key']
        issue_last_updated = issue['fields']['updated']
        
        attachments = issue['fields'].get('attachment', [])
        
        for attachment in attachments:
            self.process_attachment(
                attachment,
                issue_key,
                project_key,
                project_name,
                status,
                status_category,
                status_category_key,
                issue_last_updated,
                duplicate_groups,
                scan_stats,
                scan_id
            )
    
    def process_attachment(self, attachment: dict, issue_key: str,
                          project_key: str, project_name: str,
                          status: str, status_category: str,
                          status_category_key: str, issue_last_updated: str,
                          duplicate_groups: dict, scan_stats: dict, scan_id: str):
        """Process a single attachment."""
        # Extract metadata
        attachment_id = attachment['id']
        file_name = attachment['filename']
        file_size = attachment['size']
        mime_type = attachment['mimeType']
        content_url = attachment['content']
        created = attachment['created']
        author = attachment['author']['displayName']
        author_id = attachment['author']['accountId']
        
        # Calculate hash
        file_hash = self.calculate_hash(content_url)
        file_extension = self.get_file_extension(file_name)
        
        # Check if duplicate
        if file_hash in duplicate_groups:
            # DUPLICATE
            group = duplicate_groups[file_hash]
            group['duplicate_count'] += 1
            group['total_wasted_space'] += file_size
            
            if len(group['locations']) < 20:
                group['locations'].append({
                    'issue_key': issue_key,
                    'project_key': project_key,
                    'attachment_id': attachment_id,
                    'is_canonical': False,
                    'date_added': created,
                    'author': author
                })
            
            scan_stats['duplicate_files'] += 1
            scan_stats['duplicate_size'] += file_size
        else:
            # CANONICAL
            duplicate_groups[file_hash] = {
                'file_name': file_name,
                'file_size': file_size,
                'mime_type': mime_type,
                'canonical_issue_key': issue_key,
                'canonical_attachment_id': attachment_id,
                'duplicate_count': 0,
                'total_wasted_space': 0,
                'author': author,
                'author_id': author_id,
                'created': created,
                'status': status,
                'status_category': status_category,
                'status_category_key': status_category_key,
                'issue_last_updated': issue_last_updated,
                'locations': [{
                    'issue_key': issue_key,
                    'project_key': project_key,
                    'attachment_id': attachment_id,
                    'is_canonical': True,
                    'date_added': created,
                    'author': author
                }]
            }
            
            scan_stats['canonical_files'] += 1
        
        # Update global stats
        scan_stats['total_files'] += 1
        scan_stats['total_size'] += file_size
        
        # Update project stats
        if project_key not in scan_stats['project_stats']:
            scan_stats['project_stats'][project_key] = {
                'project_name': project_name,
                'total_size': 0,
                'duplicate_size': 0,
                'file_count': 0,
                'duplicate_count': 0
            }
        
        project_stats = scan_stats['project_stats'][project_key]
        project_stats['total_size'] += file_size
        project_stats['file_count'] += 1
        
        # Update file type stats
        if file_extension not in scan_stats['file_type_stats']:
            scan_stats['file_type_stats'][file_extension] = {
                'total_size': 0,
                'count': 0
            }
        
        file_type_stats = scan_stats['file_type_stats'][file_extension]
        file_type_stats['total_size'] += file_size
        file_type_stats['count'] += 1
    
    def calculate_hash(self, content_url: str) -> str:
        """Calculate SHA-256 hash from content URL."""
        return hashlib.sha256(content_url.encode('utf-8')).hexdigest()
    
    def get_file_extension(self, file_name: str) -> str:
        """Extract file extension."""
        if '.' in file_name:
            return file_name.rsplit('.', 1)[1].lower()
        return 'no-extension'
    
    def calculate_quick_wins(self, duplicate_groups: dict) -> List[dict]:
        """Calculate top 3 files with highest impact."""
        quick_wins = []
        
        for file_hash, group in duplicate_groups.items():
            if group['duplicate_count'] > 0:
                quick_wins.append({
                    'hash': file_hash,
                    'file_name': group['file_name'],
                    'file_size': group['file_size'],
                    'duplicate_count': group['duplicate_count'],
                    'total_wasted_space': group['total_wasted_space']
                })
        
        # Sort by wasted space (highest first)
        quick_wins.sort(key=lambda x: x['total_wasted_space'], reverse=True)
        
        return quick_wins[:3]
    
    def format_bytes(self, bytes_value: int) -> str:
        """Format bytes as human-readable string."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.2f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.2f} PB"


def main():
    """Main entry point."""
    # Configuration
    JIRA_URL = 'https://your-domain.atlassian.net'
    JIRA_EMAIL = 'your-email@example.com'
    JIRA_API_TOKEN = 'your-api-token'
    
    # Initialize components
    jira_client = JiraClient(JIRA_URL, JIRA_EMAIL, JIRA_API_TOKEN)
    storage_manager = StorageManager()
    scanner = AttachmentScanner(jira_client, storage_manager)
    
    # Run scan
    results = scanner.scan()
    
    # Print summary
    print("\n=== SCAN SUMMARY ===")
    print(f"Scan ID: {results['scan_state']['scan_id']}")
    print(f"Duration: {results['scan_state']['duration_ms']/1000:.1f}s")
    print(f"Total Storage: {scanner.format_bytes(results['scan_stats']['total_size'])}")
    print(f"Duplicate Storage: {scanner.format_bytes(results['scan_stats']['duplicate_size'])}")
    print(f"Waste Percentage: {(results['scan_stats']['duplicate_size'] / results['scan_stats']['total_size'] * 100):.1f}%")
    
    print("\n=== QUICK WINS ===")
    for i, win in enumerate(results['quick_wins'], 1):
        print(f"{i}. {win['file_name']}")
        print(f"   Duplicates: {win['duplicate_count']}")
        print(f"   Wasted: {scanner.format_bytes(win['total_wasted_space'])}")


if __name__ == '__main__':
    main()
```

---

## Performance Optimization

### 1. Parallel Processing

Use threading or asyncio for concurrent API requests:

```python
import asyncio
import aiohttp

class AsyncJiraClient:
    """Async Jira client for parallel requests."""
    
    def __init__(self, base_url: str, email: str, api_token: str):
        self.base_url = base_url.rstrip('/')
        self.auth = aiohttp.BasicAuth(email, api_token)
    
    async def fetch_issues_parallel(self, batch_ranges: List[tuple]):
        """Fetch multiple batches in parallel."""
        async with aiohttp.ClientSession(auth=self.auth) as session:
            tasks = [
                self.fetch_batch(session, start, size)
                for start, size in batch_ranges
            ]
            return await asyncio.gather(*tasks)
    
    async def fetch_batch(self, session, start_at: int, max_results: int):
        """Fetch single batch."""
        url = f"{self.base_url}/rest/api/3/search/jql"
        payload = {
            'jql': 'created >= -7300d ORDER BY created DESC',
            'startAt': start_at,
            'maxResults': max_results,
            'fields': ['key', 'attachment', 'project', 'status', 'updated']
        }
        
        async with session.post(url, json=payload) as response:
            data = await response.json()
            return data.get('issues', [])
```

### 2. Batch Database Writes

```python
def save_duplicate_groups_batch(self, scan_id: str, duplicate_groups: dict):
    """Save duplicate groups in batch for better performance."""
    cursor = self.conn.cursor()
    
    # Prepare batch data
    batch_data = [
        (scan_id, file_hash, json.dumps(group))
        for file_hash, group in duplicate_groups.items()
    ]
    
    # Batch insert
    cursor.executemany('''
        INSERT OR REPLACE INTO duplicate_groups 
        (scan_id, file_hash, group_json)
        VALUES (?, ?, ?)
    ''', batch_data)
    
    self.conn.commit()
```

### 3. Memory Management

For large instances, process in chunks to avoid memory issues:

```python
def process_large_scan(self):
    """Process scan with memory-efficient chunking."""
    # Save duplicate groups every N batches
    SAVE_INTERVAL = 10
    batch_count = 0
    
    while start_at < total_issues:
        # Process batch...
        
        batch_count += 1
        if batch_count % SAVE_INTERVAL == 0:
            # Save and clear memory
            self.storage.save_progress(scan_state, scan_stats, duplicate_groups)
            duplicate_groups.clear()  # Free memory
            # Reload only what's needed
```

---

## Error Handling

### Comprehensive Error Handling

```python
class ScanError(Exception):
    """Base exception for scan errors."""
    pass

class APIError(ScanError):
    """Jira API error."""
    pass

class StorageError(ScanError):
    """Storage operation error."""
    pass

def scan_with_error_handling(self) -> dict:
    """Execute scan with comprehensive error handling."""
    try:
        return self.scan()
    
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            raise APIError("Authentication failed. Check credentials.")
        elif e.response.status_code == 403:
            raise APIError("Permission denied. Check API token permissions.")
        elif e.response.status_code == 429:
            raise APIError("Rate limit exceeded. Please wait and try again.")
        else:
            raise APIError(f"API error: {e}")
    
    except requests.exceptions.ConnectionError:
        raise APIError("Connection error. Check network and Jira URL.")
    
    except sqlite3.Error as e:
        raise StorageError(f"Database error: {e}")
    
    except Exception as e:
        raise ScanError(f"Unexpected error: {e}")
```

### Retry Logic

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
def fetch_with_retry(self, endpoint: str, **kwargs):
    """Fetch with automatic retry on failure."""
    return self.jira.post(endpoint, **kwargs)
```

---

## Testing Strategy

### Unit Tests

```python
import unittest
from unittest.mock import Mock, patch

class TestAttachmentScanner(unittest.TestCase):
    def setUp(self):
        self.jira_client = Mock()
        self.storage_manager = Mock()
        self.scanner = AttachmentScanner(self.jira_client, self.storage_manager)
    
    def test_calculate_hash(self):
        """Test hash calculation."""
        url = "https://example.com/attachment/12345"
        hash1 = self.scanner.calculate_hash(url)
        hash2 = self.scanner.calculate_hash(url)
        
        # Same URL should produce same hash
        self.assertEqual(hash1, hash2)
        
        # Hash should be 64 characters (SHA-256 hex)
        self.assertEqual(len(hash1), 64)
    
    def test_get_file_extension(self):
        """Test file extension extraction."""
        self.assertEqual(self.scanner.get_file_extension('report.pdf'), 'pdf')
        self.assertEqual(self.scanner.get_file_extension('image.PNG'), 'png')
        self.assertEqual(self.scanner.get_file_extension('noextension'), 'no-extension')
    
    def test_duplicate_detection(self):
        """Test duplicate detection logic."""
        duplicate_groups = {}
        scan_stats = self.scanner.initialize_stats()
        
        # First attachment (canonical)
        attachment1 = {
            'id': '12345',
            'filename': 'report.pdf',
            'size': 1000000,
            'mimeType': 'application/pdf',
            'content': 'https://example.com/12345',
            'created': '2024-01-01T00:00:00Z',
            'author': {'displayName': 'John', 'accountId': 'acc1'}
        }
        
        self.scanner.process_attachment(
            attachment1, 'PROJ-1', 'PROJ', 'Project',
            'Open', 'To Do', 'new', '2024-01-01T00:00:00Z',
            duplicate_groups, scan_stats, 'scan1'
        )
        
        # Second attachment (duplicate - same content URL)
        attachment2 = {
            'id': '67890',
            'filename': 'report.pdf',
            'size': 1000000,
            'mimeType': 'application/pdf',
            'content': 'https://example.com/12345',  # Same URL
            'created': '2024-01-02T00:00:00Z',
            'author': {'displayName': 'Jane', 'accountId': 'acc2'}
        }
        
        self.scanner.process_attachment(
            attachment2, 'PROJ-2', 'PROJ', 'Project',
            'Open', 'To Do', 'new', '2024-01-02T00:00:00Z',
            duplicate_groups, scan_stats, 'scan1'
        )
        
        # Verify duplicate detection
        self.assertEqual(scan_stats['canonical_files'], 1)
        self.assertEqual(scan_stats['duplicate_files'], 1)
        self.assertEqual(scan_stats['duplicate_size'], 1000000)
```

### Integration Tests

```python
class TestIntegration(unittest.TestCase):
    @patch('requests.Session')
    def test_full_scan_flow(self, mock_session):
        """Test complete scan flow."""
        # Mock API responses
        mock_session.return_value.post.side_effect = [
            # Approximate count response
            Mock(json=lambda: {'count': 100}),
            # Search response
            Mock(json=lambda: {'issues': [/* mock issues */]})
        ]
        
        # Run scan
        scanner = AttachmentScanner(jira_client, storage_manager)
        results = scanner.scan()
        
        # Verify results
        self.assertEqual(results['scan_state']['status'], 'completed')
        self.assertGreater(results['scan_stats']['total_files'], 0)
```

---

## Deployment Considerations

### 1. Configuration Management

```python
import os
from dotenv import load_dotenv

def load_config():
    """Load configuration from environment variables."""
    load_dotenv()
    
    return {
        'jira_url': os.getenv('JIRA_URL'),
        'jira_email': os.getenv('JIRA_EMAIL'),
        'jira_api_token': os.getenv('JIRA_API_TOKEN'),
        'db_path': os.getenv('DB_PATH', 'attachment_architect.db'),
        'batch_size': int(os.getenv('BATCH_SIZE', '250')),
        'rate_limit': int(os.getenv('RATE_LIMIT', '10'))
    }
```

### 2. Logging

```python
import logging

def setup_logging():
    """Configure logging."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('scanner.log'),
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger('attachment_architect')
```

### 3. CLI Interface

```python
import argparse

def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description='Scan Jira instance for duplicate attachments'
    )
    
    parser.add_argument('--url', required=True, help='Jira instance URL')
    parser.add_argument('--email', required=True, help='Jira user email')
    parser.add_argument('--token', required=True, help='Jira API token')
    parser.add_argument('--db', default='scan.db', help='Database path')
    parser.add_argument('--batch-size', type=int, default=250, help='Batch size')
    
    return parser.parse_args()
```

### 4. Docker Deployment

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "scanner.py"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  scanner:
    build: .
    environment:
      - JIRA_URL=${JIRA_URL}
      - JIRA_EMAIL=${JIRA_EMAIL}
      - JIRA_API_TOKEN=${JIRA_API_TOKEN}
    volumes:
      - ./data:/app/data
```

---

## Key Differences from Forge Implementation

### 1. Authentication
- **Forge**: Uses `.asApp()` and `.asUser()` with automatic token management
- **Python**: Requires explicit API token or OAuth setup

### 2. Storage
- **Forge**: Forge Key-Value Storage with 240KB limit per key
- **Python**: SQLite, PostgreSQL, or file-based storage (no size limits)

### 3. Execution Model
- **Forge**: Serverless functions with webhook-based self-invocation
- **Python**: Traditional script execution (can be scheduled with cron/systemd)

### 4. Rate Limiting
- **Forge**: Automatic handling by platform
- **Python**: Must implement manual rate limiting

### 5. Progress Tracking
- **Forge**: Real-time updates via frontend polling
- **Python**: Console output or separate monitoring system

---

## Performance Benchmarks

### Expected Performance (Python Implementation)

| Instance Size | Issues | Attachments | Scan Time | Throughput |
|--------------|--------|-------------|-----------|------------|
| Small | 1,000 | 500 | ~30 sec | 33 issues/sec |
| Medium | 10,000 | 5,000 | ~5 min | 33 issues/sec |
| Large | 100,000 | 50,000 | ~50 min | 33 issues/sec |
| Enterprise | 1,000,000 | 500,000 | ~8 hours | 35 issues/sec |

### Optimization Tips

1. **Use async/await**: 3-5x faster with parallel requests
2. **Batch database writes**: 2-3x faster storage operations
3. **Connection pooling**: Reduces API overhead
4. **Memory management**: Process in chunks for large instances
5. **Caching**: Cache project/user metadata to reduce API calls

---

## Conclusion

This guide provides a complete blueprint for porting the Attachment Architect scanning capability to Python. The core algorithm remains the same:

1. **Fetch issues in batches** from Jira API
2. **Calculate SHA-256 hashes** for each attachment
3. **Detect duplicates** by comparing hashes
4. **Aggregate statistics** by project, user, file type, etc.
5. **Generate insights** (Quick Wins, waste percentage, etc.)

The Python implementation offers more flexibility in deployment options, storage backends, and integration with existing systems, while maintaining the same high performance and accuracy as the original Forge implementation.

---

**Last Updated**: January 2025  
**Version**: 1.0  
**Author**: Attachment Architect Team  
**License**: Commercial
