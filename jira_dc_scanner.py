#!/usr/bin/env python3
"""
Jira Data Center Attachment Analysis Tool
Analyzes on-premise Jira instances for duplicate attachments and storage waste.

Author: Attachment Architect Team
Version: 1.0.0
License: Commercial
"""

import hashlib
import time
import json
import sqlite3
import os
import sys
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Tuple, Set
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urljoin

import requests
from requests.auth import HTTPBasicAuth
from tqdm import tqdm
import yaml
from dotenv import load_dotenv


# ============================================================================
# Configuration and Setup
# ============================================================================

def setup_logging(config: dict) -> logging.Logger:
    """Configure logging system."""
    log_config = config.get('logging', {})
    log_level = getattr(logging, log_config.get('level', 'INFO'))
    
    # Create logs directory
    log_file = log_config.get('file', './logs/scanner.log')
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    # Configure logging
    handlers = []
    
    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(log_level)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))
    handlers.append(file_handler)
    
    # Console handler (if enabled)
    if log_config.get('console', True):
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_handler.setFormatter(logging.Formatter(
            '%(levelname)s: %(message)s'
        ))
        handlers.append(console_handler)
    
    # Configure root logger
    logging.basicConfig(
        level=log_level,
        handlers=handlers
    )
    
    return logging.getLogger('jira_dc_scanner')


def load_configuration() -> dict:
    """Load configuration from YAML file and environment variables."""
    # Load environment variables
    load_dotenv()
    
    # Load YAML configuration
    config_path = Path('config.yaml')
    if config_path.exists():
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
    else:
        config = {}
    
    # Override with environment variables
    config['jira'] = config.get('jira', {})
    config['jira']['base_url'] = os.getenv('JIRA_BASE_URL', config['jira'].get('base_url', ''))
    config['jira']['token'] = os.getenv('JIRA_TOKEN')
    config['jira']['username'] = os.getenv('JIRA_USERNAME')
    config['jira']['password'] = os.getenv('JIRA_PASSWORD')
    
    # Validate required configuration
    if not config['jira']['base_url']:
        raise ValueError("JIRA_BASE_URL must be set in .env file or config.yaml")
    
    if not config['jira']['token'] and not (config['jira']['username'] and config['jira']['password']):
        raise ValueError("Either JIRA_TOKEN or JIRA_USERNAME+JIRA_PASSWORD must be set")
    
    return config


# ============================================================================
# Rate Limiter
# ============================================================================

class RateLimiter:
    """Rate limiter to prevent overwhelming the Jira server."""
    
    def __init__(self, max_requests_per_second: int = 50):
        self.max_requests = max_requests_per_second
        self.min_interval = 1.0 / max_requests_per_second
        self.last_request_time = 0
    
    def wait_if_needed(self):
        """Wait if necessary to respect rate limit."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_interval:
            sleep_time = self.min_interval - time_since_last
            time.sleep(sleep_time)
        
        self.last_request_time = time.time()


# ============================================================================
# Jira Data Center API Client
# ============================================================================

class JiraDataCenterClient:
    """
    API client for Jira Data Center (API v2).
    
    Features:
    - Personal Access Token or Basic Authentication
    - Connection pooling
    - Rate limiting
    - Retry logic
    - Streaming downloads
    """
    
    def __init__(self, base_url: str, token: str = None, 
                 username: str = None, password: str = None,
                 verify_ssl: bool = True, rate_limit: int = 50):
        self.base_url = base_url.rstrip('/')
        self.verify_ssl = verify_ssl
        self.rate_limiter = RateLimiter(rate_limit)
        
        # Create session with connection pooling
        self.session = requests.Session()
        
        # Configure authentication
        if token:
            # Personal Access Token (recommended for DC 8.14+)
            self.session.headers.update({
                'Authorization': f'Bearer {token}'
            })
        elif username and password:
            # Basic Authentication
            self.session.auth = HTTPBasicAuth(username, password)
        else:
            raise ValueError("Either token or username+password must be provided")
        
        # Set common headers
        self.session.headers.update({
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
        
        # Configure connection pooling
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=20,
            pool_maxsize=20,
            max_retries=3
        )
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)
    
    def _make_request(self, method: str, endpoint: str, **kwargs):
        """Make HTTP request with rate limiting and error handling."""
        self.rate_limiter.wait_if_needed()
        
        url = urljoin(self.base_url, endpoint)
        kwargs['verify'] = self.verify_ssl
        
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                raise Exception("Authentication failed. Check your credentials.")
            elif e.response.status_code == 403:
                raise Exception("Permission denied. Check API token permissions.")
            elif e.response.status_code == 429:
                raise Exception("Rate limit exceeded. Please wait and try again.")
            else:
                raise Exception(f"API error: {e}")
        except requests.exceptions.ConnectionError:
            raise Exception("Connection error. Check network and Jira URL.")
    
    def get(self, endpoint: str, **kwargs):
        """Make GET request."""
        response = self._make_request('GET', endpoint, **kwargs)
        return response.json()
    
    def post(self, endpoint: str, **kwargs):
        """Make POST request."""
        response = self._make_request('POST', endpoint, **kwargs)
        return response.json()
    
    def get_total_issue_count(self, jql: str) -> int:
        """
        Get total count of issues matching JQL.
        
        Uses maxResults=0 trick since DC doesn't have approximate-count endpoint.
        """
        data = self.get('/rest/api/2/search', params={
            'jql': jql,
            'maxResults': 0,
            'fields': 'key'
        })
        return data.get('total', 0)
    
    def search_issues(self, jql: str, start_at: int = 0, 
                     max_results: int = 100, fields: List[str] = None) -> dict:
        """
        Search issues using JQL with pagination.
        
        Args:
            jql: JQL query string
            start_at: Starting index for pagination
            max_results: Maximum results to return
            fields: List of fields to include
            
        Returns:
            dict: Search results with issues array
        """
        if fields is None:
            fields = ['key', 'attachment', 'project', 'status', 'updated']
        
        params = {
            'jql': jql,
            'startAt': start_at,
            'maxResults': max_results,
            'fields': ','.join(fields)
        }
        
        return self.get('/rest/api/2/search', params=params)
    
    def download_attachment(self, url: str, stream: bool = True, 
                          timeout: int = 300) -> requests.Response:
        """
        Download attachment with streaming support.
        
        Args:
            url: Attachment content URL
            stream: Whether to stream the response
            timeout: Request timeout in seconds
            
        Returns:
            requests.Response: Response object with content
        """
        self.rate_limiter.wait_if_needed()
        
        response = self.session.get(
            url,
            stream=stream,
            timeout=timeout,
            verify=self.verify_ssl
        )
        response.raise_for_status()
        return response
    
    def test_connection(self) -> bool:
        """Test connection and authentication."""
        try:
            self.get('/rest/api/2/myself')
            return True
        except Exception as e:
            logging.error(f"Connection test failed: {e}")
            return False


# ============================================================================
# Streaming Hash Calculator
# ============================================================================

class StreamingHasher:
    """Calculate file hash without loading entire file in memory."""
    
    @staticmethod
    def hash_from_stream(file_stream, chunk_size: int = 8192) -> str:
        """
        Calculate SHA-256 hash from stream.
        
        Args:
            file_stream: Iterable of byte chunks
            chunk_size: Bytes to read per iteration
            
        Returns:
            str: Hexadecimal hash
        """
        hasher = hashlib.sha256()
        
        for chunk in file_stream:
            if chunk:  # Filter out keep-alive chunks
                hasher.update(chunk)
        
        return hasher.hexdigest()
    
    @staticmethod
    def hash_from_url(url: str) -> str:
        """
        Calculate hash from URL (fast fallback method).
        
        Args:
            url: Content URL
            
        Returns:
            str: Hexadecimal hash
        """
        return hashlib.sha256(url.encode('utf-8')).hexdigest()


# ============================================================================
# Storage Manager
# ============================================================================

class StorageManager:
    """Manages scan data persistence using SQLite."""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        
        # Create directory if needed
        os.makedirs(os.path.dirname(db_path) or '.', exist_ok=True)
        
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self.create_tables()
    
    def create_tables(self):
        """Create database schema."""
        cursor = self.conn.cursor()
        
        # Scans table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scans (
                scan_id TEXT PRIMARY KEY,
                status TEXT,
                total_issues INTEGER,
                processed_issues INTEGER,
                start_time TEXT,
                completion_time TEXT,
                duration_ms INTEGER,
                jql_query TEXT,
                config_json TEXT
            )
        ''')
        
        # Scan statistics table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS scan_stats (
                scan_id TEXT PRIMARY KEY,
                total_files INTEGER,
                total_size INTEGER,
                canonical_files INTEGER,
                duplicate_files INTEGER,
                duplicate_size INTEGER,
                project_stats_json TEXT,
                file_type_stats_json TEXT,
                FOREIGN KEY (scan_id) REFERENCES scans(scan_id)
            )
        ''')
        
        # Duplicate groups table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS duplicate_groups (
                scan_id TEXT,
                file_hash TEXT,
                file_name TEXT,
                file_size INTEGER,
                mime_type TEXT,
                canonical_issue_key TEXT,
                canonical_attachment_id TEXT,
                duplicate_count INTEGER,
                total_wasted_space INTEGER,
                author TEXT,
                author_id TEXT,
                created TEXT,
                status TEXT,
                status_category TEXT,
                status_category_key TEXT,
                issue_last_updated TEXT,
                locations_json TEXT,
                PRIMARY KEY (scan_id, file_hash),
                FOREIGN KEY (scan_id) REFERENCES scans(scan_id)
            )
        ''')
        
        # Checkpoint table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS checkpoints (
                scan_id TEXT PRIMARY KEY,
                last_processed_issue_key TEXT,
                last_start_at INTEGER,
                processed_attachment_ids TEXT,
                checkpoint_time TEXT,
                FOREIGN KEY (scan_id) REFERENCES scans(scan_id)
            )
        ''')
        
        # Create indexes for performance
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_duplicate_groups_scan 
            ON duplicate_groups(scan_id)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_duplicate_groups_hash 
            ON duplicate_groups(file_hash)
        ''')
        
        self.conn.commit()
    
    def save_scan_state(self, scan_state: dict):
        """Save or update scan state."""
        cursor = self.conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO scans 
            (scan_id, status, total_issues, processed_issues, start_time, 
             completion_time, duration_ms, jql_query, config_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            scan_state['scan_id'],
            scan_state['status'],
            scan_state['total_issues'],
            scan_state['processed_issues'],
            scan_state['start_time'],
            scan_state.get('completion_time'),
            scan_state.get('duration_ms'),
            scan_state.get('jql_query'),
            json.dumps(scan_state.get('config', {}))
        ))
        
        self.conn.commit()
    
    def save_scan_stats(self, scan_id: str, scan_stats: dict):
        """Save scan statistics."""
        cursor = self.conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO scan_stats 
            (scan_id, total_files, total_size, canonical_files, 
             duplicate_files, duplicate_size, project_stats_json, file_type_stats_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            scan_id,
            scan_stats['total_files'],
            scan_stats['total_size'],
            scan_stats['canonical_files'],
            scan_stats['duplicate_files'],
            scan_stats['duplicate_size'],
            json.dumps(scan_stats.get('project_stats', {})),
            json.dumps(scan_stats.get('file_type_stats', {}))
        ))
        
        self.conn.commit()
    
    def save_duplicate_groups(self, scan_id: str, duplicate_groups: dict):
        """Save duplicate groups in batch."""
        cursor = self.conn.cursor()
        
        # Prepare batch data
        batch_data = []
        for file_hash, group in duplicate_groups.items():
            batch_data.append((
                scan_id,
                file_hash,
                group['file_name'],
                group['file_size'],
                group['mime_type'],
                group['canonical_issue_key'],
                group['canonical_attachment_id'],
                group['duplicate_count'],
                group['total_wasted_space'],
                group['author'],
                group['author_id'],
                group['created'],
                group['status'],
                group['status_category'],
                group['status_category_key'],
                group['issue_last_updated'],
                json.dumps(group['locations'])
            ))
        
        # Batch insert
        cursor.executemany('''
            INSERT OR REPLACE INTO duplicate_groups 
            (scan_id, file_hash, file_name, file_size, mime_type,
             canonical_issue_key, canonical_attachment_id, duplicate_count,
             total_wasted_space, author, author_id, created, status,
             status_category, status_category_key, issue_last_updated, locations_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', batch_data)
        
        self.conn.commit()
    
    def save_checkpoint(self, scan_id: str, last_issue_key: str, 
                       last_start_at: int, processed_attachment_ids: Set[str]):
        """Save checkpoint for resume capability."""
        cursor = self.conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO checkpoints 
            (scan_id, last_processed_issue_key, last_start_at, 
             processed_attachment_ids, checkpoint_time)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            scan_id,
            last_issue_key,
            last_start_at,
            json.dumps(list(processed_attachment_ids)),
            datetime.now(timezone.utc).isoformat()
        ))
        
        self.conn.commit()
    
    def load_checkpoint(self, scan_id: str) -> Optional[dict]:
        """Load checkpoint to resume scan."""
        cursor = self.conn.cursor()
        
        cursor.execute('''
            SELECT * FROM checkpoints WHERE scan_id = ?
        ''', (scan_id,))
        
        row = cursor.fetchone()
        if row:
            return {
                'last_issue_key': row['last_processed_issue_key'],
                'last_start_at': row['last_start_at'],
                'processed_attachment_ids': set(json.loads(row['processed_attachment_ids'])),
                'checkpoint_time': row['checkpoint_time']
            }
        return None
    
    def get_duplicate_groups(self, scan_id: str) -> dict:
        """Load duplicate groups from database."""
        cursor = self.conn.cursor()
        
        cursor.execute('''
            SELECT * FROM duplicate_groups WHERE scan_id = ?
        ''', (scan_id,))
        
        duplicate_groups = {}
        for row in cursor.fetchall():
            file_hash = row['file_hash']
            duplicate_groups[file_hash] = {
                'file_name': row['file_name'],
                'file_size': row['file_size'],
                'mime_type': row['mime_type'],
                'canonical_issue_key': row['canonical_issue_key'],
                'canonical_attachment_id': row['canonical_attachment_id'],
                'duplicate_count': row['duplicate_count'],
                'total_wasted_space': row['total_wasted_space'],
                'author': row['author'],
                'author_id': row['author_id'],
                'created': row['created'],
                'status': row['status'],
                'status_category': row['status_category'],
                'status_category_key': row['status_category_key'],
                'issue_last_updated': row['issue_last_updated'],
                'locations': json.loads(row['locations_json'])
            }
        
        return duplicate_groups
    
    def find_incomplete_scans(self) -> List[dict]:
        """Find all incomplete scans."""
        cursor = self.conn.cursor()
        
        cursor.execute('''
            SELECT scan_id, start_time, processed_issues, total_issues, jql_query
            FROM scans 
            WHERE status = 'running' 
            ORDER BY start_time DESC
        ''')
        
        scans = []
        for row in cursor.fetchall():
            scans.append({
                'scan_id': row['scan_id'],
                'start_time': row['start_time'],
                'processed_issues': row['processed_issues'],
                'total_issues': row['total_issues'],
                'jql_query': row['jql_query']
            })
        
        return scans
    
    def list_all_scans(self) -> List[dict]:
        """List all scans (completed and incomplete)."""
        cursor = self.conn.cursor()
        
        cursor.execute('''
            SELECT s.scan_id, s.status, s.start_time, s.completion_time, 
                   s.duration_ms, s.processed_issues, s.total_issues,
                   ss.total_files, ss.total_size
            FROM scans s
            LEFT JOIN scan_stats ss ON s.scan_id = ss.scan_id
            ORDER BY s.start_time DESC
        ''')
        
        scans = []
        for row in cursor.fetchall():
            scans.append({
                'scan_id': row['scan_id'],
                'status': row['status'],
                'start_time': row['start_time'],
                'completion_time': row['completion_time'],
                'duration_ms': row['duration_ms'],
                'processed_issues': row['processed_issues'],
                'total_issues': row['total_issues'],
                'total_files': row['total_files'],
                'total_size': row['total_size']
            })
        
        return scans
    
    def reset_scan(self, scan_id: str):
        """Delete all data for a specific scan."""
        cursor = self.conn.cursor()
        
        cursor.execute('DELETE FROM checkpoints WHERE scan_id = ?', (scan_id,))
        cursor.execute('DELETE FROM duplicate_groups WHERE scan_id = ?', (scan_id,))
        cursor.execute('DELETE FROM scan_stats WHERE scan_id = ?', (scan_id,))
        cursor.execute('DELETE FROM scans WHERE scan_id = ?', (scan_id,))
        
        self.conn.commit()
    
    def reset_all_incomplete_scans(self):
        """Delete all incomplete scans."""
        cursor = self.conn.cursor()
        
        # Get all incomplete scan IDs
        cursor.execute("SELECT scan_id FROM scans WHERE status = 'running'")
        scan_ids = [row['scan_id'] for row in cursor.fetchall()]
        
        # Delete each one
        for scan_id in scan_ids:
            self.reset_scan(scan_id)
    
    def cleanup_old_scans(self, keep_days: int = 30):
        """Delete completed scans older than specified days."""
        cursor = self.conn.cursor()
        
        cutoff_date = (datetime.now(timezone.utc) - timedelta(days=keep_days)).isoformat()
        
        cursor.execute('''
            SELECT scan_id FROM scans 
            WHERE status = 'completed' AND completion_time < ?
        ''', (cutoff_date,))
        
        scan_ids = [row['scan_id'] for row in cursor.fetchall()]
        
        for scan_id in scan_ids:
            self.reset_scan(scan_id)
        
        return len(scan_ids)
    
    def close(self):
        """Close database connection."""
        self.conn.close()


# ============================================================================
# Download Manager (Multi-threaded)
# ============================================================================

class DownloadManager:
    """
    Manages parallel attachment downloads.
    
    This is THE performance game-changer.
    Uses thread pool to download multiple files simultaneously.
    """
    
    def __init__(self, jira_client: JiraDataCenterClient, 
                 num_workers: int = 12, max_file_size: int = 5 * 1024**3,
                 timeout: int = 300, use_content_hash: bool = True):
        self.jira_client = jira_client
        self.executor = ThreadPoolExecutor(max_workers=num_workers)
        self.max_file_size = max_file_size
        self.timeout = timeout
        self.use_content_hash = use_content_hash
        self.logger = logging.getLogger('jira_dc_scanner.download')
    
    def download_and_hash_batch(self, attachments: List[dict]) -> List[Tuple[str, str, dict]]:
        """
        Download and hash multiple attachments in parallel.
        
        Args:
            attachments: List of attachment metadata dicts
            
        Returns:
            List of (attachment_id, file_hash, metadata) tuples
        """
        futures = []
        
        for attachment in attachments:
            future = self.executor.submit(
                self._download_and_hash_single,
                attachment
            )
            futures.append((future, attachment))
        
        results = []
        for future, attachment in futures:
            try:
                result = future.result()
                if result:
                    results.append(result)
            except Exception as e:
                self.logger.error(
                    f"Failed to process attachment {attachment.get('id')}: {e}"
                )
                # Use URL-based hash as fallback
                try:
                    url_hash = StreamingHasher.hash_from_url(attachment['content'])
                    results.append((attachment['id'], url_hash, attachment))
                except Exception as e2:
                    self.logger.error(f"Fallback hash also failed: {e2}")
        
        return results
    
    def _download_and_hash_single(self, attachment: dict) -> Optional[Tuple[str, str, dict]]:
        """
        Download single file and calculate hash.
        
        Args:
            attachment: Attachment metadata
            
        Returns:
            Tuple of (attachment_id, file_hash, metadata) or None if failed
        """
        attachment_id = attachment['id']
        file_size = attachment['size']
        content_url = attachment['content']
        file_name = attachment.get('filename', 'unknown')
        
        # Skip files that are too large
        if file_size > self.max_file_size:
            self.logger.warning(
                f"Skipping large file: {file_name} "
                f"({self._format_bytes(file_size)})"
            )
            # Use URL hash for large files
            url_hash = StreamingHasher.hash_from_url(content_url)
            return (attachment_id, url_hash, attachment)
        
        try:
            if self.use_content_hash:
                # Download and hash actual content
                response = self.jira_client.download_attachment(
                    content_url,
                    stream=True,
                    timeout=self.timeout
                )
                
                file_hash = StreamingHasher.hash_from_stream(
                    response.iter_content(chunk_size=8192)
                )
            else:
                # Use URL-based hash (faster, less accurate)
                file_hash = StreamingHasher.hash_from_url(content_url)
            
            return (attachment_id, file_hash, attachment)
            
        except requests.exceptions.ChunkedEncodingError as e:
            # Handle "Response ended prematurely" errors
            self.logger.warning(
                f"Download incomplete for {file_name}: {e}. Using URL hash as fallback."
            )
            try:
                url_hash = StreamingHasher.hash_from_url(content_url)
                return (attachment_id, url_hash, attachment)
            except Exception as e2:
                self.logger.error(f"Fallback hash failed for {file_name}: {e2}")
                return None
                
        except requests.exceptions.Timeout as e:
            self.logger.warning(
                f"Download timeout for {file_name}: {e}. Using URL hash as fallback."
            )
            try:
                url_hash = StreamingHasher.hash_from_url(content_url)
                return (attachment_id, url_hash, attachment)
            except Exception as e2:
                self.logger.error(f"Fallback hash failed for {file_name}: {e2}")
                return None
                
        except Exception as e:
            self.logger.warning(
                f"Download failed for {file_name}: {e}. Using URL hash as fallback."
            )
            # Try URL-based hash as fallback
            try:
                url_hash = StreamingHasher.hash_from_url(content_url)
                return (attachment_id, url_hash, attachment)
            except Exception as e2:
                self.logger.error(f"Fallback hash failed for {file_name}: {e2}")
                return None
    def _format_bytes(self, bytes_value: int) -> str:
        """Format bytes as human-readable string."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.2f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.2f} PB"
    
    def shutdown(self):
        """Shutdown thread pool."""
        self.executor.shutdown(wait=True)


# ============================================================================
# Main Scanner Class
# ============================================================================

class AttachmentScanner:
    """Main scanner class that orchestrates the scanning process."""
    
    def __init__(self, jira_client: JiraDataCenterClient, 
                 storage_manager: StorageManager, config: dict):
        self.jira = jira_client
        self.storage = storage_manager
        self.config = config
        self.logger = logging.getLogger('jira_dc_scanner')
        
        # Extract configuration
        scan_config = config.get('scan', {})
        self.batch_size = scan_config.get('batch_size', 100)
        self.checkpoint_interval = config.get('storage', {}).get('checkpoint_interval', 100)
        
        # Initialize download manager
        self.download_manager = DownloadManager(
            jira_client,
            num_workers=scan_config.get('thread_pool_size', 12),
            max_file_size=scan_config.get('max_file_size_gb', 5) * 1024**3,
            timeout=scan_config.get('download_timeout_seconds', 300),
            use_content_hash=scan_config.get('use_content_hash', True)
        )
    
    def build_jql_query(self) -> str:
        """Build JQL query based on filters or custom JQL."""
        filters = self.config.get('filters', {})
        
        # Check for custom JQL first (overrides all other filters)
        custom_jql = filters.get('custom_jql')
        if custom_jql:
            self.logger.info(f"Using custom JQL query: {custom_jql}")
            # Ensure ORDER BY is present for consistent pagination
            if 'ORDER BY' not in custom_jql.upper():
                custom_jql += " ORDER BY created DESC"
            return custom_jql
        
        # Build JQL from standard filters
        jql_parts = []
        
        # Project filter
        projects = filters.get('projects', [])
        if projects:
            project_list = ', '.join(projects)
            jql_parts.append(f"project in ({project_list})")
        
        # Date range filter
        date_from = filters.get('date_from')
        if date_from:
            jql_parts.append(f"created >= '{date_from}'")
        
        date_to = filters.get('date_to')
        if date_to:
            jql_parts.append(f"created <= '{date_to}'")
        
        # Default: last 20 years if no date filter
        if not date_from and not date_to:
            jql_parts.append("created >= -7300d")
        
        # Combine with AND
        jql = ' AND '.join(jql_parts) if jql_parts else "created >= -7300d"
        jql += " ORDER BY created DESC"
        
        return jql

    def scan(self, resume: bool = False, scan_id: str = None) -> dict:
        """
        Execute full scan of Jira instance.
        
        Args:
            resume: Whether to resume from checkpoint
            scan_id: Scan ID to resume (if resume=True)
            
        Returns:
            dict: Scan results
        """
        # Build JQL query
        jql = self.build_jql_query()
        self.logger.info(f"JQL Query: {jql}")
        
        # Initialize or resume scan
        if resume and scan_id:
            scan_state, duplicate_groups, scan_stats = self._resume_scan(scan_id, jql)
        else:
            scan_state, duplicate_groups, scan_stats = self._initialize_scan(jql)
        
        scan_id = scan_state['scan_id']
        total_issues = scan_state['total_issues']
        start_at = scan_state.get('last_start_at', 0)
        
        self.logger.info(f"Starting scan {scan_id}")
        self.logger.info(f"Total issues to process: {total_issues}")
        
        if resume:
            self.logger.info(f"Resuming from issue {start_at}")
        
        # Initialize progress bar
        pbar = tqdm(
            total=total_issues,
            initial=scan_state['processed_issues'],
            desc="Analyzing Issues",
            unit="issues",
            bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]'
        )
        
        # Process in batches
        issues_since_checkpoint = 0
        
        try:
            while start_at < total_issues:
                # Fetch batch
                self.logger.debug(f"Fetching batch starting at {start_at}")
                
                try:
                    result = self.jira.search_issues(
                        jql=jql,
                        start_at=start_at,
                        max_results=self.batch_size
                    )
                    issues = result.get('issues', [])
                except Exception as e:
                    self.logger.error(f"Failed to fetch batch: {e}")
                    break
                
                if not issues:
                    self.logger.info("No more issues to process")
                    break
                
                # Process each issue
                for issue in issues:
                    self._process_issue(
                        issue,
                        duplicate_groups,
                        scan_stats,
                        scan_id
                    )
                
                # Update progress
                scan_state['processed_issues'] += len(issues)
                scan_state['last_start_at'] = start_at
                issues_since_checkpoint += len(issues)
                
                pbar.update(len(issues))
                pbar.set_postfix({
                    'files': scan_stats['total_files'],
                    'dupes': scan_stats['duplicate_files'],
                    'waste': self._format_bytes(scan_stats['duplicate_size'])
                })
                
                # Save checkpoint periodically
                if issues_since_checkpoint >= self.checkpoint_interval:
                    self.logger.debug("Saving checkpoint...")
                    self._save_progress(scan_state, scan_stats, duplicate_groups)
                    issues_since_checkpoint = 0
                
                # Move to next batch
                start_at += self.batch_size
                
        except KeyboardInterrupt:
            self.logger.warning("Scan interrupted by user")
            pbar.close()
            self._save_progress(scan_state, scan_stats, duplicate_groups)
            raise
        except Exception as e:
            self.logger.error(f"Scan failed: {e}", exc_info=True)
            pbar.close()
            self._save_progress(scan_state, scan_stats, duplicate_groups)
            raise
        
        pbar.close()
        
        # Finalize scan
        self.logger.info("Finalizing scan...")
        results = self._finalize_scan(scan_state, scan_stats, duplicate_groups)
        
        # Shutdown download manager
        self.download_manager.shutdown()
        
        return results
    
    def _initialize_scan(self, jql: str) -> Tuple[dict, dict, dict]:
        """Initialize new scan."""
        import uuid
        
        scan_id = str(uuid.uuid4())[:8]
        
        # Get total issue count
        self.logger.info("Counting total issues...")
        total_issues = self.jira.get_total_issue_count(jql)
        
        scan_state = {
            'scan_id': scan_id,
            'status': 'running',
            'total_issues': total_issues,
            'processed_issues': 0,
            'start_time': datetime.now(timezone.utc).isoformat(),
            'jql_query': jql,
            'config': self.config,
            'last_start_at': 0
        }
        
        duplicate_groups = {}
        scan_stats = self._initialize_stats()
        
        # Save initial state
        self.storage.save_scan_state(scan_state)
        
        return scan_state, duplicate_groups, scan_stats
    
    def _resume_scan(self, scan_id: str, jql: str) -> Tuple[dict, dict, dict]:
        """Resume scan from checkpoint."""
        # Load scan state from database
        cursor = self.storage.conn.cursor()
        cursor.execute('SELECT * FROM scans WHERE scan_id = ?', (scan_id,))
        row = cursor.fetchone()
        
        if not row:
            raise ValueError(f"Scan state not found for scan {scan_id}")
        
        # Try to load checkpoint (may not exist if scan was interrupted early)
        checkpoint = self.storage.load_checkpoint(scan_id)
        
        if checkpoint:
            self.logger.info(f"Loading checkpoint from {checkpoint['checkpoint_time']}")
            last_start_at = checkpoint['last_start_at']
        else:
            self.logger.warning(f"No checkpoint found for scan {scan_id}, resuming from scan state")
            # Resume from where processed_issues indicates
            last_start_at = row['processed_issues']
        
        scan_state = {
            'scan_id': scan_id,
            'status': 'running',
            'total_issues': row['total_issues'],
            'processed_issues': row['processed_issues'],
            'start_time': row['start_time'],
            'jql_query': jql,
            'config': self.config,
            'last_start_at': last_start_at
        }
        
        # Load duplicate groups (may be empty if no checkpoint)
        duplicate_groups = self.storage.get_duplicate_groups(scan_id)
        
        # Load scan stats (may not exist if no checkpoint)
        cursor.execute('SELECT * FROM scan_stats WHERE scan_id = ?', (scan_id,))
        stats_row = cursor.fetchone()
        
        if stats_row:
            scan_stats = {
                'total_files': stats_row['total_files'],
                'total_size': stats_row['total_size'],
                'canonical_files': stats_row['canonical_files'],
                'duplicate_files': stats_row['duplicate_files'],
                'duplicate_size': stats_row['duplicate_size'],
                'project_stats': json.loads(stats_row['project_stats_json']),
                'file_type_stats': json.loads(stats_row['file_type_stats_json'])
            }
        else:
            self.logger.warning("No scan stats found, starting fresh")
            scan_stats = self._initialize_stats()
        
        return scan_state, duplicate_groups, scan_stats
    
    def _initialize_stats(self) -> dict:
        """Initialize statistics structure."""
        return {
            'total_files': 0,
            'total_size': 0,
            'canonical_files': 0,
            'duplicate_files': 0,
            'duplicate_size': 0,
            'project_stats': {},
            'file_type_stats': {}
        }
    
    def _process_issue(self, issue: dict, duplicate_groups: dict,
                      scan_stats: dict, scan_id: str):
        """Process a single issue and its attachments."""
        issue_key = issue['key']
        fields = issue['fields']
        
        # Extract issue metadata
        project = fields.get('project', {})
        project_key = project.get('key', 'UNKNOWN')
        project_name = project.get('name', 'Unknown Project')
        
        status = fields.get('status', {})
        status_name = status.get('name', 'Unknown')
        status_category = status.get('statusCategory', {})
        status_category_name = status_category.get('name', 'Unknown')
        status_category_key = status_category.get('key', 'unknown')
        
        issue_last_updated = fields.get('updated', '')
        
        # Get attachments
        attachments = fields.get('attachment', [])
        
        if not attachments:
            return
        
        # Download and hash attachments in parallel
        results = self.download_manager.download_and_hash_batch(attachments)
        
        # Process results
        for attachment_id, file_hash, attachment in results:
            self._process_attachment_result(
                attachment,
                file_hash,
                issue_key,
                project_key,
                project_name,
                status_name,
                status_category_name,
                status_category_key,
                issue_last_updated,
                duplicate_groups,
                scan_stats
            )
    
    def _process_attachment_result(self, attachment: dict, file_hash: str,
                                   issue_key: str, project_key: str, project_name: str,
                                   status: str, status_category: str, status_category_key: str,
                                   issue_last_updated: str, duplicate_groups: dict, scan_stats: dict):
        """Process attachment hash result and update statistics."""
        # Extract attachment metadata
        attachment_id = attachment['id']
        file_name = attachment['filename']
        file_size = attachment['size']
        mime_type = attachment.get('mimeType', 'unknown')
        created = attachment['created']
        
        author = attachment.get('author', {})
        author_name = author.get('displayName', 'Unknown')
        author_id = author.get('name', author.get('key', 'unknown'))
        
        # Extract file extension
        file_extension = self._get_file_extension(file_name)
        
        # Check if duplicate
        if file_hash in duplicate_groups:
            # DUPLICATE FILE
            group = duplicate_groups[file_hash]
            group['duplicate_count'] += 1
            group['total_wasted_space'] += file_size
            
            # Store location (limit to 20)
            if len(group['locations']) < 20:
                group['locations'].append({
                    'issue_key': issue_key,
                    'project_key': project_key,
                    'attachment_id': attachment_id,
                    'is_canonical': False,
                    'date_added': created,
                    'author': author_name
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
                'author': author_name,
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
                    'author': author_name
                }]
            }
            
            scan_stats['canonical_files'] += 1
        
        # Update global statistics
        scan_stats['total_files'] += 1
        scan_stats['total_size'] += file_size
        
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
    
    def _get_file_extension(self, file_name: str) -> str:
        """Extract file extension."""
        if '.' in file_name:
            return file_name.rsplit('.', 1)[1].lower()
        return 'no-extension'
    
    def _save_progress(self, scan_state: dict, scan_stats: dict, duplicate_groups: dict):
        """Save current progress."""
        scan_id = scan_state['scan_id']
        
        # Save scan state
        self.storage.save_scan_state(scan_state)
        
        # Save statistics
        self.storage.save_scan_stats(scan_id, scan_stats)
        
        # Save duplicate groups
        self.storage.save_duplicate_groups(scan_id, duplicate_groups)
        
        # Save checkpoint for resume capability
        last_issue_key = scan_state.get('last_issue_key', '')
        last_start_at = scan_state.get('last_start_at', 0)
        processed_attachment_ids = set()  # We don't track individual attachments currently
        
        self.storage.save_checkpoint(
            scan_id,
            last_issue_key,
            last_start_at,
            processed_attachment_ids
        )
    
    def _finalize_scan(self, scan_state: dict, scan_stats: dict, 
                      duplicate_groups: dict) -> dict:
        """Finalize scan and calculate insights."""
        end_time = datetime.now(timezone.utc)
        start_time = datetime.fromisoformat(scan_state['start_time'])
        duration_ms = int((end_time - start_time).total_seconds() * 1000)
        
        scan_state['status'] = 'completed'
        scan_state['completion_time'] = end_time.isoformat()
        scan_state['duration_ms'] = duration_ms
        
        # Calculate insights
        quick_wins = self._calculate_quick_wins(duplicate_groups)
        
        results = {
            'scan_state': scan_state,
            'scan_stats': scan_stats,
            'duplicate_groups': duplicate_groups,
            'quick_wins': quick_wins
        }
        
        # Save final results
        self._save_progress(scan_state, scan_stats, duplicate_groups)
        
        # Print summary
        self._print_summary(results)
        
        return results
    
    def _calculate_quick_wins(self, duplicate_groups: dict) -> List[dict]:
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
    
    def _print_summary(self, results: dict):
        """Print scan summary."""
        scan_state = results['scan_state']
        scan_stats = results['scan_stats']
        quick_wins = results['quick_wins']
        
        print("\n" + "="*70)
        print("SCAN SUMMARY")
        print("="*70)
        print(f"Scan ID: {scan_state['scan_id']}")
        print(f"Duration: {scan_state['duration_ms']/1000:.1f} seconds")
        print(f"Issues Processed: {scan_state['processed_issues']:,}")
        print(f"\nTotal Files: {scan_stats['total_files']:,}")
        print(f"Total Storage: {self._format_bytes(scan_stats['total_size'])}")
        print(f"\nCanonical Files: {scan_stats['canonical_files']:,}")
        print(f"Duplicate Files: {scan_stats['duplicate_files']:,}")
        print(f"Duplicate Storage: {self._format_bytes(scan_stats['duplicate_size'])}")
        
        if scan_stats['total_size'] > 0:
            waste_pct = (scan_stats['duplicate_size'] / scan_stats['total_size']) * 100
            print(f"Waste Percentage: {waste_pct:.1f}%")
        
        if quick_wins:
            print(f"\n{'='*70}")
            print("QUICK WINS (Top 3 Duplicate Files)")
            print("="*70)
            for i, win in enumerate(quick_wins, 1):
                print(f"\n{i}. {win['file_name']}")
                print(f"   File Size: {self._format_bytes(win['file_size'])}")
                print(f"   Duplicates: {win['duplicate_count']}")
                print(f"   Wasted Space: {self._format_bytes(win['total_wasted_space'])}")
        
        print("\n" + "="*70)
    
    def _format_bytes(self, bytes_value: int) -> str:
        """Format bytes as human-readable string."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_value < 1024.0:
                return f"{bytes_value:.2f} {unit}"
            bytes_value /= 1024.0
        return f"{bytes_value:.2f} PB"


# ============================================================================
# Main Entry Point
# ============================================================================

def format_bytes(bytes_value: int) -> str:
    """Format bytes as human-readable string."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.2f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.2f} PB"


def main():
    """Main entry point."""
    import argparse
    
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description='Jira Data Center Attachment Analysis Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Start new scan (auto-resumes if incomplete scan found)
  python jira_dc_scanner.py
  
  # Resume specific scan
  python jira_dc_scanner.py --resume <scan_id>
  
  # Reset and start fresh
  python jira_dc_scanner.py --reset
  
  # Reset specific scan
  python jira_dc_scanner.py --reset <scan_id>
  
  # List all scans
  python jira_dc_scanner.py --list
  
  # Cleanup old completed scans (>30 days)
  python jira_dc_scanner.py --cleanup
        '''
    )
    parser.add_argument('--resume', metavar='SCAN_ID', help='Resume scan from checkpoint')
    parser.add_argument('--reset', nargs='?', const=True, metavar='SCAN_ID',
                       help='Reset scan (delete checkpoint). Use without SCAN_ID to reset all incomplete scans.')
    parser.add_argument('--list', action='store_true', help='List all scans')
    parser.add_argument('--cleanup', type=int, nargs='?', const=30, metavar='DAYS',
                       help='Cleanup completed scans older than DAYS (default: 30)')
    args = parser.parse_args()
    
    print("="*70)
    print("Jira Data Center Attachment Analysis Tool")
    print("Version 1.0.0")
    print("="*70)
    print()
    
    try:
        # Load configuration
        print("Loading configuration...")
        config = load_configuration()
        
        # Setup logging
        logger = setup_logging(config)
        logger.info("Starting Jira Data Center Attachment Scanner")
        
        # Initialize storage (needed for --list, --reset, --cleanup commands)
        db_path = config.get('storage', {}).get('database_path', './scans/scan.db')
        storage_manager = StorageManager(db_path)
        
        # Handle --list command
        if args.list:
            print("\n" + "="*70)
            print("ALL SCANS")
            print("="*70)
            scans = storage_manager.list_all_scans()
            if not scans:
                print("No scans found.")
            else:
                for scan in scans:
                    print(f"\nScan ID: {scan['scan_id']}")
                    print(f"  Status: {scan['status']}")
                    print(f"  Started: {scan['start_time']}")
                    if scan['completion_time']:
                        print(f"  Completed: {scan['completion_time']}")
                        print(f"  Duration: {scan['duration_ms']/1000:.1f}s")
                    print(f"  Progress: {scan['processed_issues']}/{scan['total_issues']} issues")
                    if scan['total_files']:
                        print(f"  Files: {scan['total_files']:,} ({format_bytes(scan['total_size'])})")
            storage_manager.close()
            return 0
        
        # Handle --cleanup command
        if args.cleanup:
            print(f"\nCleaning up scans older than {args.cleanup} days...")
            deleted_count = storage_manager.cleanup_old_scans(args.cleanup)
            print(f"✓ Deleted {deleted_count} old scan(s)")
            storage_manager.close()
            return 0
        
        # Handle --reset command
        if args.reset:
            if args.reset is True:
                # Reset all incomplete scans
                print("\nResetting all incomplete scans...")
                storage_manager.reset_all_incomplete_scans()
                print("✓ All incomplete scans have been reset")
            else:
                # Reset specific scan
                print(f"\nResetting scan {args.reset}...")
                storage_manager.reset_scan(args.reset)
                print(f"✓ Scan {args.reset} has been reset")
            storage_manager.close()
            return 0
        
        # Initialize components for actual scanning
        print("Connecting to Jira...")
        jira_client = JiraDataCenterClient(
            base_url=config['jira']['base_url'],
            token=config['jira'].get('token'),
            username=config['jira'].get('username'),
            password=config['jira'].get('password'),
            verify_ssl=config['jira'].get('verify_ssl', True),
            rate_limit=config.get('scan', {}).get('rate_limit_per_second', 50)
        )
        
        # Test connection
        if not jira_client.test_connection():
            print("ERROR: Failed to connect to Jira. Check your credentials.")
            storage_manager.close()
            return 1
        
        print("✓ Connected successfully")
        
        # Initialize scanner
        scanner = AttachmentScanner(jira_client, storage_manager, config)
        
        # Run scan (with resume if specified)
        if args.resume:
            print(f"\nResuming scan {args.resume}...\n")
            results = scanner.scan(resume=True, scan_id=args.resume)
        else:
            print("\nStarting new scan...\n")
            results = scanner.scan()
        
        # Export results
        print("\nExporting results...")
        output_dir = config.get('output', {}).get('output_dir', './reports')
        os.makedirs(output_dir, exist_ok=True)
        
        # Export JSON
        json_path = os.path.join(output_dir, f"scan_{results['scan_state']['scan_id']}.json")
        with open(json_path, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"✓ JSON report saved to: {json_path}")
        
        # Generate HTML visual analysis report
        print("\nGenerating visual analysis report...")
        try:
            from generate_visual_analysis_report import generate_report
            html_path = json_path.replace('.json', '_visual_analysis.html')
            generate_report(results, html_path)
            print(f"✓ Visual analysis report saved to: {html_path}")
            print(f"\n📊 Open the report in your browser:")
            print(f"   {os.path.abspath(html_path)}")
        except Exception as e:
            print(f"⚠ Warning: Could not generate visual report: {e}")
        
        # Close storage
        storage_manager.close()
        
        print("\n✅ Scan completed successfully!")
        return 0
        
    except KeyboardInterrupt:
        print("\n\nScan interrupted by user.")
        return 130
    except Exception as e:
        print(f"\nERROR: {e}")
        logging.error("Fatal error", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())
