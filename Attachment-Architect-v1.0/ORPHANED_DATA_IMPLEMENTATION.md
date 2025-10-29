# Orphaned Data Risk Report - Implementation Status

## ✅ COMPLETED

### 1. Backend Functionality (`generate_visual_analysis_report.py`)
- ✅ Added `fetch_active_users_from_jira()` function
  - Queries Jira API `/rest/api/2/user/search` for active users
  - Handles pagination (1000 users per batch)
  - Supports both token and basic auth
  - Returns set of active user IDs

- ✅ Updated `calculate_user_stats()` function
  - Now accepts `active_users` parameter
  - Compares attachment authors against active users
  - Separates active vs inactive users
  - Returns tuple: `(all_users, orphaned_stats)`

- ✅ Created `orphaned_stats` dictionary structure:
  ```python
  {
      'total_storage': int,        # Total bytes of orphaned data
      'total_files': int,           # Total orphaned files
      'inactive_user_count': int,   # Number of inactive users
      'top_inactive_users': [       # Top 5 inactive users
          {
              'user_id': str,
              'display_name': str,
              'total_storage': int,
              'file_count': int
          }
      ]
  }
  ```

- ✅ Integrated into `generate_report()` function
  - Fetches active users automatically
  - Passes orphaned_stats to HTML generator

## 🔄 TODO - HTML Display

### 2. Update `generate_html_content.py`

Need to update the function signature and add HTML section:

```python
def generate_html(scan_state, projects_data, top_file_types, top_storage_users,
                  age_stats, status_stats, frozen_dinosaurs, remaining_files,
                  total_storage, total_files, min_file_size_mb, min_days_inactive,
                  orphaned_stats=None):  # ADD THIS PARAMETER
```

### 3. Add Orphaned Data Section to HTML

Add this section in the "By User" tab, BEFORE the top storage users chart:

```html
<!-- Orphaned Data Risk Report (if available) -->
{% if orphaned_stats %}
<div style="background: #fff3cd; border-left: 4px solid #ff9800; padding: 20px; border-radius: 6px; margin-bottom: 30px;">
    <h4 style="color: #ff6f00; margin-bottom: 15px; font-size: 20px;">
        ⚠️ Orphaned Data Risk Report
    </h4>
    
    <!-- KPI -->
    <div style="background: white; padding: 20px; border-radius: 6px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
        <div style="font-size: 48px; font-weight: bold; color: #d32f2f; margin-bottom: 10px;">
            {format_bytes(orphaned_stats['total_storage'])}
        </div>
        <div style="font-size: 18px; color: #666; margin-bottom: 5px;">
            of attachment data is "orphaned"
        </div>
        <div style="font-size: 14px; color: #999;">
            Owned by {orphaned_stats['inactive_user_count']} inactive or deleted users
            ({orphaned_stats['total_files']:,} files)
        </div>
    </div>
    
    <!-- Top 5 Inactive Users Table -->
    <h5 style="margin-bottom: 15px; color: #333;">Top 5 Inactive Users - Data Left Behind:</h5>
    <table style="width: 100%; border-collapse: collapse;">
        <thead>
            <tr style="background: #f5f5f5;">
                <th style="padding: 12px; text-align: left; border-bottom: 2px solid #ddd;">User</th>
                <th style="padding: 12px; text-align: right; border-bottom: 2px solid #ddd;">Files</th>
                <th style="padding: 12px; text-align: right; border-bottom: 2px solid #ddd;">Storage</th>
            </tr>
        </thead>
        <tbody>
            {% for user in orphaned_stats['top_inactive_users'] %}
            <tr>
                <td style="padding: 12px; border-bottom: 1px solid #eee;">
                    <strong>{user['display_name']}</strong><br>
                    <span style="font-size: 12px; color: #999;">({user['user_id']})</span>
                </td>
                <td style="padding: 12px; text-align: right; border-bottom: 1px solid #eee;">
                    {user['file_count']:,}
                </td>
                <td style="padding: 12px; text-align: right; border-bottom: 1px solid #eee; font-weight: bold;">
                    {format_bytes(user['total_storage'])}
                </td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
    
    <div style="margin-top: 15px; padding: 15px; background: #fff; border-radius: 4px; font-size: 13px; color: #666;">
        <strong>⚠️ Security Risk:</strong> Orphaned data may contain sensitive information from former employees.
        Consider archiving or deleting this data as part of your data governance policy.
    </div>
</div>
{% endif %}
```

### 4. Update CSV Export (`generate_csv_export.py`)

Add new CSV export function:

```python
def export_orphaned_data(results, output_path, orphaned_stats):
    """Export orphaned data analysis to CSV."""
    if not orphaned_stats:
        return
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # Summary
        writer.writerow(['Metric', 'Value'])
        writer.writerow(['Total Orphaned Storage (bytes)', orphaned_stats['total_storage']])
        writer.writerow(['Total Orphaned Storage (formatted)', format_bytes(orphaned_stats['total_storage'])])
        writer.writerow(['Total Orphaned Files', orphaned_stats['total_files']])
        writer.writerow(['Inactive User Count', orphaned_stats['inactive_user_count']])
        writer.writerow([''])
        
        # Top inactive users
        writer.writerow(['User ID', 'Display Name', 'File Count', 'Total Storage (bytes)', 'Total Storage (formatted)'])
        for user in orphaned_stats['top_inactive_users']:
            writer.writerow([
                user['user_id'],
                user['display_name'],
                user['file_count'],
                user['total_storage'],
                format_bytes(user['total_storage'])
            ])
```

Add to `export_all_csv()`:
```python
# 11. Orphaned Data (if available)
if orphaned_stats:
    orphaned_path = os.path.join(output_dir, f"scan_{scan_id}_orphaned_data.csv")
    export_orphaned_data(results, orphaned_path, orphaned_stats)
    csv_files.append(orphaned_path)
```

## ��� Expected Output

### Console Output:
```
📡 Fetching active users from Jira...
  Fetched 1000 users (total: 1000)
  Fetched 523 users (total: 1523)
✓ Found 1523 active users in Jira
```

### HTML Report:
- Yellow warning box at top of "By User" tab
- Large KPI showing total orphaned storage (e.g., "45.2 GB")
- Subtitle: "Owned by 23 inactive or deleted users (1,234 files)"
- Table showing top 5 inactive users with their data

### CSV Export:
- New file: `scan_XXXXXXXX_orphaned_data.csv`
- Summary metrics + top inactive users table

## 🎯 Benefits

1. **Security Risk Identification:** Highlights data from former employees
2. **Compliance:** Helps meet data retention policies
3. **Cost Savings:** Identifies cleanup opportunities
4. **Governance:** Supports data ownership policies

## 🔒 Privacy Note

The feature only identifies inactive users - it does NOT delete or modify any data. Admins must manually review and take action based on the report.
