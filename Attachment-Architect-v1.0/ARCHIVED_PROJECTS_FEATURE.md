# Archived Projects Analysis Feature - Implementation Guide

## Overview
This feature identifies attachments in archived Jira projects - the **safest and fastest cleanup candidates**.

## Implementation Steps

### 1. Add Helper Function to get Jira Session

Add this function after `format_bytes()` in `generate_visual_analysis_report.py`:

```python
def get_jira_session():
    """
    Create and return a Jira session with credentials.
    Returns tuple of (session, base_url) or (None, None) if credentials not available.
    """
    try:
        import os
        import requests
        from requests.auth import HTTPBasicAuth
        
        # Try to load dotenv if available
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            pass
        
        # Load credentials from environment
        base_url = os.getenv('JIRA_BASE_URL', '').rstrip('/')
        token = os.getenv('JIRA_TOKEN')
        username = os.getenv('JIRA_USERNAME')
        password = os.getenv('JIRA_PASSWORD')
        
        if not base_url:
            return None, None
        
        # Create session
        session = requests.Session()
        
        if token:
            session.headers.update({'Authorization': f'Bearer {token}'})
        elif username and password:
            session.auth = HTTPBasicAuth(username, password)
        else:
            return None, None
        
        session.headers.update({
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
        
        return session, base_url
        
    except Exception as e:
        print(f"⚠ Warning: Could not create Jira session: {e}")
        return None, None
```

### 2. Update `fetch_active_users_from_jira()` to use the helper

Replace the function with:

```python
def fetch_active_users_from_jira():
    """Fetch list of active users from Jira."""
    try:
        session, base_url = get_jira_session()
        
        if not session or not base_url:
            print("⚠ Warning: Cannot fetch active users - no Jira credentials.")
            return None
        
        print("📡 Fetching active users from Jira...")
        
        active_users = set()
        start_at = 0
        max_results = 1000
        
        while True:
            url = f"{base_url}/rest/api/2/user/search"
            params = {
                'username': '.',
                'startAt': start_at,
                'maxResults': max_results,
                'includeActive': True,
                'includeInactive': False
            }
            
            try:
                response = session.get(url, params=params, timeout=30)
                response.raise_for_status()
                users = response.json()
                
                if not users:
                    break
                
                for user in users:
                    user_id = user.get('key') or user.get('name') or user.get('accountId')
                    if user_id:
                        active_users.add(user_id)
                
                print(f"  Fetched {len(users)} users (total: {len(active_users)})")
                
                if len(users) < max_results:
                    break
                
                start_at += max_results
                
            except Exception as e:
                print(f"⚠ Warning: Failed to fetch users: {e}")
                break
        
        print(f"✓ Found {len(active_users)} active users in Jira")
        return active_users
        
    except Exception as e:
        print(f"⚠ Warning: Could not fetch active users: {e}")
        return None
```

### 3. Add New Function to Fetch Archived Projects

Add after `fetch_active_users_from_jira()`:

```python
def fetch_archived_projects_from_jira():
    """
    Fetch list of archived projects from Jira.
    Returns dict mapping project key to project info.
    """
    try:
        session, base_url = get_jira_session()
        
        if not session or not base_url:
            print("⚠ Warning: Cannot fetch archived projects - no Jira credentials.")
            return None
        
        print("📡 Fetching projects from Jira...")
        
        url = f"{base_url}/rest/api/2/project"
        
        try:
            response = session.get(url, timeout=30)
            response.raise_for_status()
            projects = response.json()
            
            archived_projects = {}
            
            for project in projects:
                project_key = project.get('key')
                project_name = project.get('name')
                is_archived = project.get('archived', False)
                
                if is_archived and project_key:
                    archived_projects[project_key] = {
                        'key': project_key,
                        'name': project_name,
                        'archived': True
                    }
            
            print(f"✓ Found {len(projects)} total projects, {len(archived_projects)} archived")
            return archived_projects
            
        except Exception as e:
            print(f"⚠ Warning: Failed to fetch projects: {e}")
            return None
        
    except Exception as e:
        print(f"⚠ Warning: Could not fetch archived projects: {e}")
        return None
```

### 4. Add Function to Calculate Archived Project Stats

Add after `calculate_age_stats()`:

```python
def calculate_archived_project_stats(duplicate_groups, project_stats, archived_projects):
    """
    Calculate statistics for archived projects.
    
    Args:
        duplicate_groups: Dictionary of file groups
        project_stats: Project statistics from scan
        archived_projects: Dict of archived projects from Jira
    
    Returns:
        Dict with archived project statistics
    """
    if not archived_projects:
        return None
    
    archived_stats = {
        'total_storage': 0,
        'total_files': 0,
        'project_count': 0,
        'projects': []
    }
    
    for project_key, stats in project_stats.items():
        if project_key in archived_projects:
            archived_stats['total_storage'] += stats['total_size']
            archived_stats['total_files'] += stats['file_count']
            archived_stats['project_count'] += 1
            
            archived_stats['projects'].append({
                'key': project_key,
                'name': archived_projects[project_key]['name'],
                'total_storage': stats['total_size'],
                'file_count': stats['file_count']
            })
    
    # Sort by storage
    archived_stats['projects'].sort(key=lambda x: x['total_storage'], reverse=True)
    
    return archived_stats if archived_stats['project_count'] > 0 else None
```

### 5. Update `generate_report()` Function

Add these lines after fetching active users:

```python
# Fetch archived projects from Jira
archived_projects = fetch_archived_projects_from_jira()

# Calculate archived project statistics
archived_project_stats = calculate_archived_project_stats(
    duplicate_groups, project_stats, archived_projects
)
```

And update the HTML generation call to include archived_project_stats:

```python
html = generate_html(
    scan_state, projects_data, top_file_types, top_storage_users,
    age_stats, status_stats, frozen_dinosaurs, remaining_files,
    total_storage, total_files, min_file_size_mb, min_days_inactive,
    orphaned_stats, archived_project_stats  # ADD THIS
)
```

### 6. Update HTML Generation

In `generate_html_content.py`, update function signature:

```python
def generate_html(scan_state, projects_data, top_file_types, top_storage_users,
                  age_stats, status_stats, frozen_dinosaurs, remaining_files,
                  total_storage, total_files, min_file_size_mb, min_days_inactive,
                  orphaned_stats=None, archived_project_stats=None):  # ADD archived_project_stats
```

Update `generate_all_tabs()` signature:

```python
def generate_all_tabs(projects_data, top_file_types, top_storage_users, age_stats, status_stats, 
                      frozen_dinosaurs, remaining_files, min_file_size_mb, min_days_inactive, 
                      orphaned_stats=None, archived_project_stats=None):  # ADD archived_project_stats
```

Update the call in `generate_html()`:

```python
{generate_all_tabs(projects_data, top_file_types, top_storage_users, age_stats, status_stats, 
                   frozen_dinosaurs, remaining_files, min_file_size_mb, min_days_inactive, 
                   orphaned_stats, archived_project_stats)}
```

Update `generate_age_tab()` signature and add archived projects section:

```python
def generate_age_tab(age_stats, archived_project_stats=None):
    """Generate age tab content with archived projects analysis."""
    html = """
            <div id="age" class="tab-content">
                <h3 style="margin-bottom: 10px;">Attachment Age Distribution</h3>
                <p style="color: #7f8c8d; margin-bottom: 20px;">Understand if your storage is consumed by recent or old files</p>
    """
    
    # Archived Projects Quick Win (if available)
    if archived_project_stats and archived_project_stats['project_count'] > 0:
        html += f"""
                <!-- Archived Projects Quick Win -->
                <div style="background: linear-gradient(135deg, #d4edda 0%, #c3e6cb 100%); border-left: 5px solid #28a745; padding: 25px; border-radius: 8px; margin-bottom: 35px; box-shadow: 0 4px 12px rgba(40, 167, 69, 0.15);">
                    <div style="display: flex; align-items: center; margin-bottom: 20px;">
                        <div style="font-size: 48px; margin-right: 15px;">🔥</div>
                        <div>
                            <h4 style="color: #155724; margin: 0; font-size: 22px; font-weight: 700;">
                                Quick Win: Archived Projects
                            </h4>
                            <p style="color: #28a745; margin: 5px 0 0 0; font-size: 14px;">
                                Safest and fastest cleanup candidates
                            </p>
                        </div>
                    </div>
                    
                    <!-- KPI Card -->
                    <div style="background: white; padding: 30px; border-radius: 8px; margin-bottom: 25px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); border: 2px solid #28a745;">
                        <div style="text-align: center;">
                            <div style="font-size: 56px; font-weight: 800; color: #28a745; margin-bottom: 10px; text-shadow: 2px 2px 4px rgba(0,0,0,0.1);">
                                {format_bytes(archived_project_stats['total_storage'])}
                            </div>
                            <div style="font-size: 20px; color: #424242; margin-bottom: 8px; font-weight: 600;">
                                of attachments within <strong style="color: #28a745;">{archived_project_stats['project_count']} archived projects</strong>
                            </div>
                            <div style="font-size: 15px; color: #666; padding: 15px; background: #f5f5f5; border-radius: 6px; margin-top: 15px;">
                                <div style="margin-bottom: 5px;">
                                    📊 <strong>{archived_project_stats['total_files']:,} files</strong> ready for safe cleanup
                                </div>
                                <div style="font-size: 13px; color: #999; margin-top: 8px;">
                                    These projects are archived and no longer active
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Top 5 Archived Projects Table -->
                    <div style="background: white; padding: 25px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
                        <h5 style="margin: 0 0 20px 0; color: #333; font-size: 18px; font-weight: 600; border-bottom: 2px solid #28a745; padding-bottom: 10px;">
                            📦 Top 5 Archived Projects by Storage
                        </h5>
                        <table style="width: 100%; border-collapse: collapse;">
                            <thead>
                                <tr style="background: #d4edda;">
                                    <th style="padding: 14px 12px; text-align: left; border-bottom: 2px solid #28a745; font-weight: 600; color: #155724; font-size: 12px; text-transform: uppercase;">
                                        Project
                                    </th>
                                    <th style="padding: 14px 12px; text-align: right; border-bottom: 2px solid #28a745; font-weight: 600; color: #155724; font-size: 12px; text-transform: uppercase;">
                                        Files
                                    </th>
                                    <th style="padding: 14px 12px; text-align: right; border-bottom: 2px solid #28a745; font-weight: 600; color: #155724; font-size: 12px; text-transform: uppercase;">
                                        Total Storage
                                    </th>
                                </tr>
                            </thead>
                            <tbody>
        """
        
        for i, project in enumerate(archived_project_stats['projects'][:5], 1):
            row_bg = '#f8f9fa' if i % 2 == 0 else 'white'
            html += f"""
                                <tr style="background: {row_bg}; transition: background 0.2s;" onmouseover="this.style.background='#e2f0e4'" onmouseout="this.style.background='{row_bg}'">
                                    <td style="padding: 16px 12px; border-bottom: 1px solid #f0f0f0;">
                                        <div style="font-weight: 600; color: #333; margin-bottom: 3px;">{project['name']}</div>
                                        <div style="font-size: 12px; color: #999; font-family: monospace;">({project['key']})</div>
                                    </td>
                                    <td style="padding: 16px 12px; text-align: right; border-bottom: 1px solid #f0f0f0; color: #666; font-weight: 500;">
                                        {project['file_count']:,}
                                    </td>
                                    <td style="padding: 16px 12px; text-align: right; border-bottom: 1px solid #f0f0f0; font-weight: 700; color: #28a745; font-size: 15px;">
                                        {format_bytes(project['total_storage'])}
                                    </td>
                                </tr>
            """
        
        html += """
                            </tbody>
                        </table>
                    </div>
                    
                    <!-- Action Items -->
                    <div style="margin-top: 20px; padding: 18px 20px; background: #e3f2fd; border-radius: 6px; border-left: 4px solid #2196f3;">
                        <div style="font-size: 14px; color: #1565c0; font-weight: 600; margin-bottom: 10px;">
                            💡 Why This is a Quick Win:
                        </div>
                        <ul style="margin: 0; padding-left: 20px; color: #424242; font-size: 13px; line-height: 1.8;">
                            <li><strong>Zero Risk:</strong> Archived projects are no longer active</li>
                            <li><strong>Fast Cleanup:</strong> Bulk delete entire project attachments</li>
                            <li><strong>Immediate Impact:</strong> Free up significant storage quickly</li>
                            <li><strong>Easy Approval:</strong> No active work will be affected</li>
                        </ul>
                    </div>
                </div>
        """
    
    # Continue with age distribution chart...
    html += """
                <h4 style="margin: 30px 0 15px 0;">Age Distribution</h4>
                <div class="bar-chart">
    """
    
    # Rest of the age tab code...
    age_order = ['0-90 days', '90-365 days', '1-2 years', '2-4 years', '>4 years']
    max_size = max([age_stats[bucket]['total_size'] for bucket in age_order]) if age_stats else 1
    
    for bucket in age_order:
        data = age_stats[bucket]
        width_pct = (data['total_size'] / max_size) * 100 if max_size > 0 else 0
        html += f"""
                    <div class="bar-item">
                        <div class="bar-label">{bucket}</div>
                        <div class="bar-track">
                            <div class="bar-fill" style="width: {width_pct}%;">
                                {data['file_count']:,} files
                            </div>
                        </div>
                        <div class="bar-value">{format_bytes(data['total_size'])}</div>
                    </div>
        """
    
    html += """
                </div>
                
                <div class="pro-tip">
                    <span class="pro-tip-icon">💡 Pro Tip:</span>
                    <span class="pro-tip-text">
                        A large amount of storage in the older categories indicates that archival policies could provide significant cost savings.
                    </span>
                </div>
            </div>
    """
    
    return html
```

## Expected Output

When you regenerate the report, you'll see in the **"📅 By Age"** tab:

✅ **Green "Quick Win" banner** at the top
✅ **Large KPI** showing total storage in archived projects
✅ **Table of top 5 archived projects** with storage amounts
✅ **"Why This is a Quick Win"** section explaining the benefits

## Console Output

```
📡 Fetching projects from Jira...
✓ Found 50 total projects, 8 archived
```

## Benefits

- **Zero Risk** - Archived projects are inactive
- **Fast Cleanup** - Bulk delete entire project attachments
- **Immediate Impact** - Free up significant storage
- **Easy Approval** - No active work affected
