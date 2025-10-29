# Archived Projects Feature - Implementation Status

## ✅ COMPLETED

### 1. Backend Functions Added
- ✅ `get_jira_session()` - Helper to create Jira session
- ✅ `fetch_active_users_from_jira()` - Simplified to use helper
- ✅ `fetch_archived_projects_from_jira()` - NEW: Fetches archived projects

## 🔄 TODO - Complete Implementation

### 2. Add Archived Project Stats Calculation

Add this function after `calculate_age_stats()` in `generate_visual_analysis_report.py`:

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

### 3. Update `generate_report()` Function

Add these lines after `active_users = fetch_active_users_from_jira()`:

```python
# Fetch archived projects from Jira
archived_projects = fetch_archived_projects_from_jira()

# Calculate archived project statistics  
archived_project_stats = calculate_archived_project_stats(
    duplicate_groups, project_stats, archived_projects
)
```

And update the HTML generation call:

```python
html = generate_html(
    scan_state, projects_data, top_file_types, top_storage_users,
    age_stats, status_stats, frozen_dinosaurs, remaining_files,
    total_storage, total_files, min_file_size_mb, min_days_inactive,
    orphaned_stats, archived_project_stats  # ADD THIS
)
```

### 4. Update HTML Generation Files

See `ARCHIVED_PROJECTS_FEATURE.md` for complete HTML implementation details.

## Quick Implementation Script

Run this to complete the implementation:

```bash
cd "c:\Users\krozenbe\Documents\Jira plugins\Attachment-Architect_python\Attachment-Architect-v1.0"

# The backend is 90% done, just need to:
# 1. Add calculate_archived_project_stats() function
# 2. Call it in generate_report()
# 3. Update HTML generation to display it
```

## Expected Result

When complete, the "By Age" tab will show:

🔥 **Quick Win: Archived Projects**
- Green banner at top
- Large KPI: "X GB of attachments within Y archived projects"
- Table of top 5 archived projects
- "Why This is a Quick Win" section

## Test Command

```bash
python generate_visual_analysis_report.py reports\scan_5eaa446a.json
```

Expected console output:
```
📡 Fetching active users from Jira...
✓ Found 2596 active users in Jira
📡 Fetching projects from Jira...
✓ Found 50 total projects, 8 archived
```
