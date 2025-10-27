"""
CSV export module for scan results
Generates multiple CSV files for different data views
"""

import csv
import os
from datetime import datetime


def format_bytes(bytes_value):
    """Format bytes as human-readable string."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.2f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.2f} PB"


def export_scan_summary(results, output_path):
    """Export scan summary to CSV."""
    scan_state = results['scan_state']
    scan_stats = results['scan_stats']
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # Header
        writer.writerow(['Metric', 'Value'])
        
        # Scan metadata
        writer.writerow(['Scan ID', scan_state['scan_id']])
        writer.writerow(['Status', scan_state['status']])
        writer.writerow(['Start Time', scan_state['start_time']])
        writer.writerow(['Completion Time', scan_state.get('completion_time', 'N/A')])
        writer.writerow(['Duration (seconds)', scan_state.get('duration_ms', 0) / 1000])
        writer.writerow(['Issues Processed', scan_state['processed_issues']])
        writer.writerow(['Total Issues', scan_state['total_issues']])
        writer.writerow([''])
        
        # Storage statistics
        writer.writerow(['Total Files', scan_stats['total_files']])
        writer.writerow(['Total Storage (bytes)', scan_stats['total_size']])
        writer.writerow(['Total Storage (formatted)', format_bytes(scan_stats['total_size'])])
        writer.writerow([''])
        
        # Duplicate statistics
        writer.writerow(['Canonical Files', scan_stats['canonical_files']])
        writer.writerow(['Duplicate Files', scan_stats['duplicate_files']])
        writer.writerow(['Duplicate Storage (bytes)', scan_stats['duplicate_size']])
        writer.writerow(['Duplicate Storage (formatted)', format_bytes(scan_stats['duplicate_size'])])
        
        if scan_stats['total_size'] > 0:
            waste_pct = (scan_stats['duplicate_size'] / scan_stats['total_size']) * 100
            writer.writerow(['Waste Percentage', f"{waste_pct:.2f}%"])


def export_duplicate_files(results, output_path):
    """Export duplicate files list to CSV."""
    duplicate_groups = results['duplicate_groups']
    
    # Filter only files with duplicates
    duplicates = {k: v for k, v in duplicate_groups.items() if v['duplicate_count'] > 0}
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # Header
        writer.writerow([
            'File Hash',
            'File Name',
            'File Size (bytes)',
            'File Size (formatted)',
            'MIME Type',
            'Duplicate Count',
            'Total Wasted Space (bytes)',
            'Total Wasted Space (formatted)',
            'Canonical Issue',
            'Canonical Attachment ID',
            'Author',
            'Created Date',
            'Status',
            'Status Category',
            'Issue Last Updated'
        ])
        
        # Sort by wasted space (highest first)
        sorted_duplicates = sorted(
            duplicates.items(),
            key=lambda x: x[1]['total_wasted_space'],
            reverse=True
        )
        
        # Write data
        for file_hash, group in sorted_duplicates:
            writer.writerow([
                file_hash,
                group['file_name'],
                group['file_size'],
                format_bytes(group['file_size']),
                group['mime_type'],
                group['duplicate_count'],
                group['total_wasted_space'],
                format_bytes(group['total_wasted_space']),
                group['canonical_issue_key'],
                group['canonical_attachment_id'],
                group['author'],
                group['created'],
                group['status'],
                group['status_category'],
                group['issue_last_updated']
            ])


def export_duplicate_locations(results, output_path):
    """Export all duplicate file locations to CSV."""
    duplicate_groups = results['duplicate_groups']
    
    # Filter only files with duplicates
    duplicates = {k: v for k, v in duplicate_groups.items() if v['duplicate_count'] > 0}
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # Header
        writer.writerow([
            'File Hash',
            'File Name',
            'File Size (bytes)',
            'File Size (formatted)',
            'Issue Key',
            'Project Key',
            'Attachment ID',
            'Is Canonical',
            'Date Added',
            'Author'
        ])
        
        # Sort by wasted space (highest first)
        sorted_duplicates = sorted(
            duplicates.items(),
            key=lambda x: x[1]['total_wasted_space'],
            reverse=True
        )
        
        # Write data
        for file_hash, group in sorted_duplicates:
            for location in group['locations']:
                writer.writerow([
                    file_hash,
                    group['file_name'],
                    group['file_size'],
                    format_bytes(group['file_size']),
                    location['issue_key'],
                    location['project_key'],
                    location['attachment_id'],
                    'Yes' if location['is_canonical'] else 'No',
                    location['date_added'],
                    location['author']
                ])


def export_project_stats(results, output_path):
    """Export per-project statistics to CSV."""
    scan_stats = results['scan_stats']
    project_stats = scan_stats.get('project_stats', {})
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # Header
        writer.writerow([
            'Project Key',
            'Project Name',
            'Total Files',
            'Total Storage (bytes)',
            'Total Storage (formatted)',
            'Duplicate Files',
            'Duplicate Storage (bytes)',
            'Duplicate Storage (formatted)',
            'Waste Percentage'
        ])
        
        # Sort by total storage (highest first)
        sorted_projects = sorted(
            project_stats.items(),
            key=lambda x: x[1]['total_size'],
            reverse=True
        )
        
        # Write data
        for project_key, stats in sorted_projects:
            waste_pct = 0
            if stats['total_size'] > 0:
                waste_pct = (stats['duplicate_size'] / stats['total_size']) * 100
            
            writer.writerow([
                project_key,
                stats['project_name'],
                stats['file_count'],
                stats['total_size'],
                format_bytes(stats['total_size']),
                stats['duplicate_count'],
                stats['duplicate_size'],
                format_bytes(stats['duplicate_size']),
                f"{waste_pct:.2f}%"
            ])


def export_file_type_stats(results, output_path):
    """Export per-file-type statistics to CSV."""
    scan_stats = results['scan_stats']
    file_type_stats = scan_stats.get('file_type_stats', {})
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # Header
        writer.writerow([
            'File Extension',
            'File Count',
            'Total Storage (bytes)',
            'Total Storage (formatted)',
            'Average File Size (bytes)',
            'Average File Size (formatted)'
        ])
        
        # Sort by total storage (highest first)
        sorted_types = sorted(
            file_type_stats.items(),
            key=lambda x: x[1]['total_size'],
            reverse=True
        )
        
        # Write data
        for ext, stats in sorted_types:
            avg_size = stats['total_size'] / stats['count'] if stats['count'] > 0 else 0
            
            writer.writerow([
                ext,
                stats['count'],
                stats['total_size'],
                format_bytes(stats['total_size']),
                int(avg_size),
                format_bytes(avg_size)
            ])


def export_quick_wins(results, output_path):
    """Export quick wins (top cleanup opportunities) to CSV."""
    quick_wins = results.get('quick_wins', [])
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # Header
        writer.writerow([
            'Rank',
            'File Hash',
            'File Name',
            'File Size (bytes)',
            'File Size (formatted)',
            'Duplicate Count',
            'Total Wasted Space (bytes)',
            'Total Wasted Space (formatted)',
            'Potential Savings'
        ])
        
        # Write data
        for i, win in enumerate(quick_wins, 1):
            writer.writerow([
                i,
                win['hash'],
                win['file_name'],
                win['file_size'],
                format_bytes(win['file_size']),
                win['duplicate_count'],
                win['total_wasted_space'],
                format_bytes(win['total_wasted_space']),
                f"Delete {win['duplicate_count']} duplicates to save {format_bytes(win['total_wasted_space'])}"
            ])


def export_user_stats(results, output_path):
    """Export per-user statistics to CSV."""
    duplicate_groups = results['duplicate_groups']
    
    # Aggregate by user
    user_stats = {}
    for file_hash, group in duplicate_groups.items():
        author_id = group['author_id']
        author_name = group['author']
        
        if author_id not in user_stats:
            user_stats[author_id] = {
                'author_name': author_name,
                'total_files': 0,
                'total_storage': 0,
                'canonical_files': 0,
                'duplicate_files': 0
            }
        
        # Count canonical file
        user_stats[author_id]['canonical_files'] += 1
        user_stats[author_id]['total_files'] += 1 + group['duplicate_count']
        user_stats[author_id]['total_storage'] += group['file_size'] * (1 + group['duplicate_count'])
        user_stats[author_id]['duplicate_files'] += group['duplicate_count']
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # Header
        writer.writerow([
            'User ID',
            'User Name',
            'Total Files',
            'Total Storage (bytes)',
            'Total Storage (formatted)',
            'Canonical Files',
            'Duplicate Files',
            'Average File Size (bytes)',
            'Average File Size (formatted)'
        ])
        
        # Sort by total storage (highest first)
        sorted_users = sorted(
            user_stats.items(),
            key=lambda x: x[1]['total_storage'],
            reverse=True
        )
        
        # Write data
        for user_id, stats in sorted_users:
            avg_size = stats['total_storage'] / stats['total_files'] if stats['total_files'] > 0 else 0
            
            writer.writerow([
                user_id,
                stats['author_name'],
                stats['total_files'],
                stats['total_storage'],
                format_bytes(stats['total_storage']),
                stats['canonical_files'],
                stats['duplicate_files'],
                int(avg_size),
                format_bytes(avg_size)
            ])


def export_age_stats(results, output_path):
    """Export age distribution statistics to CSV."""
    from datetime import datetime, timezone
    
    duplicate_groups = results['duplicate_groups']
    
    # Age buckets
    age_buckets = {
        '0-90 days': {'count': 0, 'size': 0},
        '90-365 days': {'count': 0, 'size': 0},
        '1-2 years': {'count': 0, 'size': 0},
        '2-4 years': {'count': 0, 'size': 0},
        '>4 years': {'count': 0, 'size': 0}
    }
    
    now = datetime.now(timezone.utc)
    
    for file_hash, group in duplicate_groups.items():
        try:
            # Parse created date
            created = datetime.fromisoformat(group['created'].replace('Z', '+00:00'))
            days_old = (now - created).days
            
            # Determine bucket
            if days_old <= 90:
                bucket = '0-90 days'
            elif days_old <= 365:
                bucket = '90-365 days'
            elif days_old <= 730:  # 2 years
                bucket = '1-2 years'
            elif days_old <= 1460:  # 4 years
                bucket = '2-4 years'
            else:
                bucket = '>4 years'
            
            # Count all instances (canonical + duplicates)
            total_instances = 1 + group['duplicate_count']
            total_size = group['file_size'] * total_instances
            
            age_buckets[bucket]['count'] += total_instances
            age_buckets[bucket]['size'] += total_size
        except:
            # If date parsing fails, skip
            pass
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # Header
        writer.writerow([
            'Age Range',
            'File Count',
            'Total Storage (bytes)',
            'Total Storage (formatted)',
            'Percentage of Files',
            'Percentage of Storage'
        ])
        
        # Calculate totals
        total_count = sum(b['count'] for b in age_buckets.values())
        total_size = sum(b['size'] for b in age_buckets.values())
        
        # Write data in order
        age_order = ['0-90 days', '90-365 days', '1-2 years', '2-4 years', '>4 years']
        for age_range in age_order:
            bucket = age_buckets[age_range]
            count_pct = (bucket['count'] / total_count * 100) if total_count > 0 else 0
            size_pct = (bucket['size'] / total_size * 100) if total_size > 0 else 0
            
            writer.writerow([
                age_range,
                bucket['count'],
                bucket['size'],
                format_bytes(bucket['size']),
                f"{count_pct:.1f}%",
                f"{size_pct:.1f}%"
            ])


def export_status_stats(results, output_path):
    """Export per-status statistics to CSV."""
    duplicate_groups = results['duplicate_groups']
    
    # Aggregate by status
    status_stats = {}
    for file_hash, group in duplicate_groups.items():
        status = group['status']
        status_category = group['status_category']
        
        if status not in status_stats:
            status_stats[status] = {
                'status_category': status_category,
                'file_count': 0,
                'total_storage': 0
            }
        
        # Count all instances (canonical + duplicates)
        total_instances = 1 + group['duplicate_count']
        total_size = group['file_size'] * total_instances
        
        status_stats[status]['file_count'] += total_instances
        status_stats[status]['total_storage'] += total_size
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # Header
        writer.writerow([
            'Status',
            'Status Category',
            'File Count',
            'Total Storage (bytes)',
            'Total Storage (formatted)',
            'Percentage of Files',
            'Percentage of Storage'
        ])
        
        # Calculate totals
        total_count = sum(s['file_count'] for s in status_stats.values())
        total_size = sum(s['total_storage'] for s in status_stats.values())
        
        # Sort by total storage (highest first)
        sorted_statuses = sorted(
            status_stats.items(),
            key=lambda x: x[1]['total_storage'],
            reverse=True
        )
        
        # Write data
        for status, stats in sorted_statuses:
            count_pct = (stats['file_count'] / total_count * 100) if total_count > 0 else 0
            size_pct = (stats['total_storage'] / total_size * 100) if total_size > 0 else 0
            
            writer.writerow([
                status,
                stats['status_category'],
                stats['file_count'],
                stats['total_storage'],
                format_bytes(stats['total_storage']),
                f"{count_pct:.1f}%",
                f"{size_pct:.1f}%"
            ])


def export_heat_index(results, output_path, min_file_size_mb=10, min_days_inactive=180):
    """Export heat index analysis to CSV."""
    from datetime import datetime, timezone
    
    duplicate_groups = results['duplicate_groups']
    
    # Calculate heat scores
    heat_index_files = []
    now = datetime.now(timezone.utc)
    
    for file_hash, group in duplicate_groups.items():
        try:
            # Parse last updated date
            last_updated = datetime.fromisoformat(group['issue_last_updated'].replace('Z', '+00:00'))
            days_inactive = (now - last_updated).days
            
            # Calculate file size in MB
            file_size_mb = group['file_size'] / (1024 * 1024)
            
            # Calculate heat score
            heat_score = (file_size_mb * days_inactive) / 1000
            
            # Include all files (not just frozen dinosaurs)
            for location in group['locations']:
                heat_index_files.append({
                    'file_hash': file_hash,
                    'file_name': group['file_name'],
                    'file_size': group['file_size'],
                    'file_size_mb': file_size_mb,
                    'issue_key': location['issue_key'],
                    'project_key': location['project_key'],
                    'attachment_id': location['attachment_id'],
                    'days_inactive': days_inactive,
                    'status': group['status'],
                    'status_category': group['status_category'],
                    'heat_score': heat_score,
                    'is_frozen_dinosaur': (file_size_mb >= min_file_size_mb and days_inactive >= min_days_inactive)
                })
        except:
            # If date parsing fails, skip
            pass
    
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        
        # Header
        writer.writerow([
            'File Hash',
            'File Name',
            'File Size (bytes)',
            'File Size (MB)',
            'File Size (formatted)',
            'Issue Key',
            'Project Key',
            'Attachment ID',
            'Days Inactive',
            'Status',
            'Status Category',
            'Heat Score',
            'Is Frozen Dinosaur'
        ])
        
        # Sort by heat score (highest first)
        heat_index_files.sort(key=lambda x: x['heat_score'], reverse=True)
        
        # Write data
        for file_data in heat_index_files:
            writer.writerow([
                file_data['file_hash'],
                file_data['file_name'],
                file_data['file_size'],
                f"{file_data['file_size_mb']:.2f}",
                format_bytes(file_data['file_size']),
                file_data['issue_key'],
                file_data['project_key'],
                file_data['attachment_id'],
                file_data['days_inactive'],
                file_data['status'],
                file_data['status_category'],
                f"{file_data['heat_score']:.2f}",
                'Yes' if file_data['is_frozen_dinosaur'] else 'No'
            ])


def export_all_csv(results, output_dir):
    """
    Export all CSV files.
    
    Args:
        results: Scan results dictionary
        output_dir: Output directory path
        
    Returns:
        List of generated file paths
    """
    scan_id = results['scan_state']['scan_id']
    
    # Create output directory if needed
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate all CSV files
    csv_files = []
    
    # 1. Scan Summary
    summary_path = os.path.join(output_dir, f"scan_{scan_id}_summary.csv")
    export_scan_summary(results, summary_path)
    csv_files.append(summary_path)
    
    # 2. Duplicate Files
    duplicates_path = os.path.join(output_dir, f"scan_{scan_id}_duplicates.csv")
    export_duplicate_files(results, duplicates_path)
    csv_files.append(duplicates_path)
    
    # 3. Duplicate Locations (detailed)
    locations_path = os.path.join(output_dir, f"scan_{scan_id}_duplicate_locations.csv")
    export_duplicate_locations(results, locations_path)
    csv_files.append(locations_path)
    
    # 4. Project Statistics
    projects_path = os.path.join(output_dir, f"scan_{scan_id}_projects.csv")
    export_project_stats(results, projects_path)
    csv_files.append(projects_path)
    
    # 5. File Type Statistics
    filetypes_path = os.path.join(output_dir, f"scan_{scan_id}_file_types.csv")
    export_file_type_stats(results, filetypes_path)
    csv_files.append(filetypes_path)
    
    # 6. Quick Wins
    quickwins_path = os.path.join(output_dir, f"scan_{scan_id}_quick_wins.csv")
    export_quick_wins(results, quickwins_path)
    csv_files.append(quickwins_path)
    
    # 7. User Statistics
    users_path = os.path.join(output_dir, f"scan_{scan_id}_users.csv")
    export_user_stats(results, users_path)
    csv_files.append(users_path)
    
    # 8. Age Distribution
    age_path = os.path.join(output_dir, f"scan_{scan_id}_age_distribution.csv")
    export_age_stats(results, age_path)
    csv_files.append(age_path)
    
    # 9. Status Distribution
    status_path = os.path.join(output_dir, f"scan_{scan_id}_status_distribution.csv")
    export_status_stats(results, status_path)
    csv_files.append(status_path)
    
    # 10. Heat Index
    heat_path = os.path.join(output_dir, f"scan_{scan_id}_heat_index.csv")
    export_heat_index(results, heat_path)
    csv_files.append(heat_path)
    
    return csv_files


if __name__ == '__main__':
    # Test with sample data
    import json
    import sys
    
    if len(sys.argv) > 1:
        json_path = sys.argv[1]
        with open(json_path, 'r') as f:
            results = json.load(f)
        
        output_dir = os.path.dirname(json_path)
        csv_files = export_all_csv(results, output_dir)
        
        print(f"✓ Generated {len(csv_files)} CSV files:")
        for csv_file in csv_files:
            print(f"  - {os.path.basename(csv_file)}")
    else:
        print("Usage: python generate_csv_export.py <json_file_path>")
