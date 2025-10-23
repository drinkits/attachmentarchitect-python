#!/usr/bin/env python3
"""
Generate Visual Analysis Report
Comprehensive storage analysis across multiple dimensions
NO duplicate detection - pure storage insights
"""

import json
import sys
import argparse
from datetime import datetime
from pathlib import Path
from collections import defaultdict


def format_bytes(bytes_value):
    """Format bytes as human-readable string."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.2f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.2f} PB"


def calculate_user_stats(duplicate_groups):
    """Calculate per-user statistics."""
    user_stats = defaultdict(lambda: {
        'total_storage': 0,
        'file_count': 0,
        'display_name': 'Unknown'
    })
    
    for file_hash, group in duplicate_groups.items():
        author_id = group.get('author_id', 'unknown')
        author_name = group.get('author', 'Unknown')
        file_size = group['file_size']
        
        user_stats[author_id]['display_name'] = author_name
        user_stats[author_id]['total_storage'] += file_size
        user_stats[author_id]['file_count'] += 1
    
    user_list = []
    for user_id, stats in user_stats.items():
        user_list.append({
            'user_id': user_id,
            'display_name': stats['display_name'],
            'total_storage': stats['total_storage'],
            'file_count': stats['file_count']
        })
    
    return sorted(user_list, key=lambda x: x['total_storage'], reverse=True)


def calculate_age_stats(duplicate_groups):
    """Calculate attachment age distribution."""
    age_buckets = {
        '0-90 days': {'min': 0, 'max': 90, 'total_size': 0, 'file_count': 0},
        '90-365 days': {'min': 90, 'max': 365, 'total_size': 0, 'file_count': 0},
        '1-2 years': {'min': 365, 'max': 730, 'total_size': 0, 'file_count': 0},
        '2-4 years': {'min': 730, 'max': 1460, 'total_size': 0, 'file_count': 0},
        '>4 years': {'min': 1460, 'max': 999999, 'total_size': 0, 'file_count': 0}
    }
    
    now = datetime.now()
    
    for file_hash, group in duplicate_groups.items():
        try:
            created = datetime.fromisoformat(group['created'].replace('Z', '+00:00'))
            days_old = (now - created).days
            file_size = group['file_size']
            
            for bucket_name, bucket_data in age_buckets.items():
                if bucket_data['min'] <= days_old < bucket_data['max']:
                    bucket_data['total_size'] += file_size
                    bucket_data['file_count'] += 1
                    break
        except:
            age_buckets['>4 years']['total_size'] += group['file_size']
            age_buckets['>4 years']['file_count'] += 1
    
    return age_buckets


def calculate_status_stats(duplicate_groups):
    """Calculate per-status statistics."""
    status_stats = defaultdict(lambda: {'total_size': 0, 'file_count': 0})
    
    for file_hash, group in duplicate_groups.items():
        status_category = group.get('status_category', 'Unknown')
        status_name = group.get('status', 'Unknown')
        file_size = group['file_size']
        
        key = f"{status_category}::{status_name}"
        status_stats[key]['total_size'] += file_size
        status_stats[key]['file_count'] += 1
        status_stats[key]['category'] = status_category
        status_stats[key]['name'] = status_name
    
    status_list = []
    for key, stats in status_stats.items():
        status_list.append({
            'category': stats['category'],
            'name': stats['name'],
            'total_size': stats['total_size'],
            'file_count': stats['file_count']
        })
    
    return sorted(status_list, key=lambda x: x['total_size'], reverse=True)


def calculate_heat_index(duplicate_groups):
    """Calculate heat index for files (size + age)."""
    heat_files = []
    from datetime import timezone
    now = datetime.now(timezone.utc)
    
    for file_hash, group in duplicate_groups.items():
        try:
            # Parse dates with timezone awareness
            created_str = group['created'].replace('Z', '+00:00')
            issue_updated_str = group['issue_last_updated'].replace('Z', '+00:00')
            
            created = datetime.fromisoformat(created_str)
            issue_updated = datetime.fromisoformat(issue_updated_str)
            
            # Calculate days since activity
            days_since_activity = (now - issue_updated).days
            file_size = group['file_size']
            
            # Heat score: (size in MB) * (days / 100)
            heat_score = (file_size / (1024 * 1024)) * (days_since_activity / 100)
            
            heat_files.append({
                'file_name': group['file_name'],
                'file_size': file_size,
                'issue_key': group['canonical_issue_key'],
                'days_since_activity': days_since_activity,
                'heat_score': heat_score,
                'status': group.get('status', 'Unknown')
            })
        except Exception as e:
            # Log error for debugging
            print(f"Warning: Failed to process file {group.get('file_name', 'unknown')}: {e}")
            pass
    
    return sorted(heat_files, key=lambda x: x['heat_score'], reverse=True)


def generate_report(scan_data, output_path, min_file_size_mb=10, min_days_inactive=365):
    """
    Generate comprehensive visual analysis report.
    
    Args:
        scan_data: Scan results data
        output_path: Output HTML file path
        min_file_size_mb: Minimum file size in MB for "Frozen Dinosaurs" (default: 10)
        min_days_inactive: Minimum days since last activity for "Frozen Dinosaurs" (default: 365)
    """
    
    scan_state = scan_data['scan_state']
    scan_stats = scan_data['scan_stats']
    duplicate_groups = scan_data['duplicate_groups']
    
    total_storage = scan_stats['total_size']
    total_files = scan_stats['total_files']
    
    project_stats = scan_stats.get('project_stats', {})
    file_type_stats = scan_stats.get('file_type_stats', {})
    
    user_stats = calculate_user_stats(duplicate_groups)
    age_stats = calculate_age_stats(duplicate_groups)
    status_stats = calculate_status_stats(duplicate_groups)
    
    heat_files = calculate_heat_index(duplicate_groups)
    
    # Filter frozen dinosaurs based on configurable criteria
    min_file_size_bytes = min_file_size_mb * 1024 * 1024
    frozen_dinosaurs = [f for f in heat_files if f['file_size'] > min_file_size_bytes and f['days_since_activity'] > min_days_inactive]
    remaining_files = [f for f in heat_files if f not in frozen_dinosaurs]
    
    # Prepare project data
    projects_data = []
    for project_key, stats in project_stats.items():
        avg_size = stats['total_size'] / stats['file_count'] if stats['file_count'] > 0 else 0
        avg_size_mb = avg_size / (1024 * 1024)
        
        if avg_size_mb < 1:
            size_color = "#a8d5ff"
        elif avg_size_mb < 5:
            size_color = "#6eb6ff"
        elif avg_size_mb < 10:
            size_color = "#3498db"
        else:
            size_color = "#0d5aa7"
        
        projects_data.append({
            'name': project_key,
            'size': stats['total_size'],
            'file_count': stats['file_count'],
            'avg_size_mb': avg_size_mb,
            'size_color': size_color
        })
    
    projects_data.sort(key=lambda x: x['size'], reverse=True)
    
    # Prepare file type data
    file_type_colors = {
        'xlsx': '#4472C4', 'xls': '#4472C4',
        'docx': '#5B9BD5', 'doc': '#5B9BD5',
        'pdf': '#70AD47',
        'png': '#FFC000', 'jpg': '#ED7D31', 'jpeg': '#ED7D31',
        'zip': '#A5A5A6', '7z': '#A5A5A6',
        'txt': '#FFC000',
        'json': '#44546A',
        'edoc': '#9E480E',
        'pptx': '#C55A11', 'ppt': '#C55A11',
        'mp4': '#843C0C',
        'dwg': '#636363'
    }
    
    file_types_data = []
    for file_ext, stats in file_type_stats.items():
        if stats['count'] > 0:
            avg_size_mb = (stats['total_size'] / stats['count']) / (1024 * 1024)
            total_size_mb = stats['total_size'] / (1024 * 1024)
            display_ext = file_ext if file_ext else 'no-ext'
            color = file_type_colors.get(file_ext, '#95A5A6')
            
            file_types_data.append({
                'ext': display_ext,
                'count': stats['count'],
                'total_size': stats['total_size'],
                'total_size_mb': total_size_mb,
                'avg_size_mb': avg_size_mb,
                'color': color
            })
    
    file_types_data.sort(key=lambda x: x['total_size'], reverse=True)
    top_file_types = file_types_data[:15]
    
    top_storage_users = user_stats[:10]
    
    # Generate HTML with all data
    from generate_html_content import generate_html
    html = generate_html(
        scan_state, projects_data, top_file_types, top_storage_users,
        age_stats, status_stats, frozen_dinosaurs, remaining_files,
        total_storage, total_files, min_file_size_mb, min_days_inactive
    )
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✓ Visual analysis report generated: {output_path}")
    print(f"  Total Storage: {format_bytes(total_storage)}")
    print(f"  Total Files: {total_files:,}")
    print(f"  Projects: {len(projects_data)}")
    print(f"  File Types: {len(file_types_data)}")
    print(f"  Frozen Dinosaurs: {len(frozen_dinosaurs)} (>{min_file_size_mb}MB, >{min_days_inactive} days)")
    print(f"  Remaining Files: {len(remaining_files)}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Generate visual analysis report from Jira attachment scan',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Basic usage
  python generate_visual_analysis_report.py scan_9f7629d1.json
  
  # Custom output file
  python generate_visual_analysis_report.py scan_9f7629d1.json report.html
  
  # Configure "Frozen Dinosaurs" criteria
  python generate_visual_analysis_report.py scan_9f7629d1.json --min-size 5 --min-days 180
        '''
    )
    
    parser.add_argument('input_file', help='Input JSON scan file')
    parser.add_argument('output_file', nargs='?', help='Output HTML file (optional)')
    parser.add_argument('--min-size', type=float, default=10, 
                       help='Minimum file size in MB for "Frozen Dinosaurs" (default: 10)')
    parser.add_argument('--min-days', type=int, default=365,
                       help='Minimum days since last activity for "Frozen Dinosaurs" (default: 365)')
    
    args = parser.parse_args()
    
    input_file = args.input_file
    output_file = args.output_file if args.output_file else input_file.replace('.json', '_visual_analysis.html')
    
    print(f"Loading scan data from: {input_file}")
    with open(input_file, 'r', encoding='utf-8') as f:
        scan_data = json.load(f)
    
    print(f"Generating visual analysis report...")
    print(f"  Frozen Dinosaurs criteria: >{args.min_size} MB and >{args.min_days} days inactive")
    generate_report(scan_data, output_file, args.min_size, args.min_days)
    
    print(f"\n✅ Visual analysis report ready! Open in browser:")
    print(f"   {Path(output_file).absolute()}")


if __name__ == '__main__':
    main()
