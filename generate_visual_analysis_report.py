#!/usr/bin/env python3
"""
Generate Visual Analysis Report
Comprehensive storage analysis across multiple dimensions
NO duplicate detection - pure storage insights
"""

import json
import sys
from datetime import datetime, timedelta
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
    
    # Convert to list and sort
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
            
            # Find appropriate bucket
            for bucket_name, bucket_data in age_buckets.items():
                if bucket_data['min'] <= days_old < bucket_data['max']:
                    bucket_data['total_size'] += file_size
                    bucket_data['file_count'] += 1
                    break
        except:
            # If date parsing fails, put in oldest bucket
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
    
    # Convert to list
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
    now = datetime.now()
    
    for file_hash, group in duplicate_groups.items():
        try:
            created = datetime.fromisoformat(group['created'].replace('Z', '+00:00'))
            issue_updated = datetime.fromisoformat(group['issue_last_updated'].replace('Z', '+00:00'))
            days_since_activity = (now - issue_updated).days
            file_size = group['file_size']
            
            # Heat score: larger files + older issues = higher heat
            # Normalize: size in MB * days / 100
            heat_score = (file_size / (1024 * 1024)) * (days_since_activity / 100)
            
            heat_files.append({
                'file_name': group['file_name'],
                'file_size': file_size,
                'issue_key': group['canonical_issue_key'],
                'days_since_activity': days_since_activity,
                'heat_score': heat_score,
                'status': group.get('status', 'Unknown')
            })
        except:
            pass
    
    return sorted(heat_files, key=lambda x: x['heat_score'], reverse=True)


def generate_report(scan_data, output_path):
    """Generate comprehensive visual analysis report."""
    
    scan_state = scan_data['scan_state']
    scan_stats = scan_data['scan_stats']
    duplicate_groups = scan_data['duplicate_groups']
    
    # Calculate all statistics
    total_storage = scan_stats['total_size']
    total_files = scan_stats['total_files']
    
    # Project stats
    project_stats = scan_stats.get('project_stats', {})
    
    # File type stats
    file_type_stats = scan_stats.get('file_type_stats', {})
    
    # Calculate user stats
    user_stats = calculate_user_stats(duplicate_groups)
    
    # Calculate age stats
    age_stats = calculate_age_stats(duplicate_groups)
    
    # Calculate status stats
    status_stats = calculate_status_stats(duplicate_groups)
    
    # Calculate heat index
    heat_files = calculate_heat_index(duplicate_groups)
    frozen_dinosaurs = [f for f in heat_files if f['file_size'] > 10*1024*1024 and f['days_since_activity'] > 365][:20]
    
    # Prepare project data
    projects_data = []
    for project_key, stats in project_stats.items():
        avg_size = stats['total_size'] / stats['file_count'] if stats['file_count'] > 0 else 0
        avg_size_mb = avg_size / (1024 * 1024)
        
        # Color based on size
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
    
    # Top users
    top_storage_users = user_stats[:10]
    
    # Generate HTML
    html = generate_html(
        scan_state, projects_data, top_file_types, top_storage_users,
        age_stats, status_stats, frozen_dinosaurs, heat_files[:50],
        total_storage, total_files
    )
    
    # Write to file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✓ Visual analysis report generated: {output_path}")
    print(f"  Total Storage: {format_bytes(total_storage)}")
    print(f"  Total Files: {total_files:,}")
    print(f"  Projects: {len(projects_data)}")
    print(f"  File Types: {len(file_types_data)}")
    print(f"  Frozen Dinosaurs: {len(frozen_dinosaurs)}")


def generate_html(scan_state, projects_data, top_file_types, top_storage_users,
                  age_stats, status_stats, frozen_dinosaurs, heat_files,
                  total_storage, total_files):
    """Generate HTML content."""
    
    # Convert data to JSON for JavaScript
    projects_json = json.dumps(projects_data)
    file_types_json = json.dumps(top_file_types)
    age_stats_json = json.dumps(age_stats)
    status_stats_json = json.dumps(status_stats)
    
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Attachment Architect - Visual Analysis</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: #f5f7fa;
            color: #2c3e50;
            line-height: 1.6;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        
        .header {{
            background: white;
            padding: 30px;
            border-radius: 8px;
            margin-bottom: 30px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        .header h1 {{
            font-size: 32px;
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 10px;
        }}
        
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .metric-card {{
            background: white;
            padding: 25px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        .metric-label {{
            font-size: 12px;
            text-transform: uppercase;
            color: #7f8c8d;
            margin-bottom: 8px;
            font-weight: 600;
            letter-spacing: 0.5px;
        }}
        
        .metric-value {{
            font-size: 36px;
            font-weight: 700;
            color: #2c3e50;
            margin-bottom: 5px;
        }}
        
        .metric-subtitle {{
            font-size: 13px;
            color: #95a5a6;
        }}
        
        .section {{
            background: white;
            padding: 30px;
            border-radius: 8px;
            margin-bottom: 30px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        
        .section-title {{
            font-size: 24px;
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 10px;
        }}
        
        .section-subtitle {{
            color: #7f8c8d;
            font-size: 14px;
            margin-bottom: 25px;
        }}
        
        .tabs {{
            display: flex;
            border-bottom: 2px solid #ecf0f1;
            margin-bottom: 25px;
            gap: 10px;
            flex-wrap: wrap;
        }}
        
        .tab {{
            padding: 12px 24px;
            cursor: pointer;
            border-bottom: 3px solid transparent;
            margin-bottom: -2px;
            color: #7f8c8d;
            font-weight: 500;
            transition: all 0.3s;
            background: none;
            border-left: none;
            border-right: none;
            border-top: none;
            font-size: 14px;
        }}
        
        .tab:hover {{
            color: #3498db;
        }}
        
        .tab.active {{
            color: #3498db;
            border-bottom-color: #3498db;
        }}
        
        .tab-content {{
            display: none;
        }}
        
        .tab-content.active {{
            display: block;
        }}
        
        .pro-tip {{
            background: #e3f2fd;
            border-left: 4px solid #2196f3;
            padding: 15px 20px;
            border-radius: 4px;
            margin-top: 20px;
        }}
        
        .pro-tip-icon {{
            color: #2196f3;
            font-weight: 600;
            margin-right: 5px;
        }}
        
        .pro-tip-text {{
            color: #1565c0;
            font-size: 14px;
        }}
        
        .pro-tip-text strong {{
            color: #0d47a1;
        }}
        
        .chart-container {{
            position: relative;
            width: 100%;
            height: 500px;
            border: 1px solid #ecf0f1;
            border-radius: 4px;
            background: #fafbfc;
            margin: 20px 0;
        }}
        
        .bar-chart {{
            padding: 20px;
        }}
        
        .bar-item {{
            display: flex;
            align-items: center;
            gap: 15px;
            margin-bottom: 15px;
        }}
        
        .bar-label {{
            min-width: 150px;
            font-size: 14px;
            font-weight: 500;
            color: #2c3e50;
        }}
        
        .bar-track {{
            flex: 1;
            height: 30px;
            background: #ecf0f1;
            border-radius: 4px;
            overflow: hidden;
        }}
        
        .bar-fill {{
            height: 100%;
            background: linear-gradient(90deg, #3498db, #2980b9);
            display: flex;
            align-items: center;
            padding: 0 10px;
            color: white;
            font-size: 12px;
            font-weight: 600;
            transition: width 0.5s ease;
        }}
        
        .bar-value {{
            min-width: 100px;
            text-align: right;
            font-size: 14px;
            font-weight: 600;
            color: #2c3e50;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}
        
        th {{
            background: #f8f9fa;
            padding: 12px;
            text-align: left;
            font-weight: 600;
            font-size: 12px;
            text-transform: uppercase;
            color: #7f8c8d;
            border-bottom: 2px solid #ecf0f1;
        }}
        
        td {{
            padding: 15px 12px;
            border-bottom: 1px solid #ecf0f1;
        }}
        
        tr:hover {{
            background: #f8f9fa;
        }}
        
        .alert {{
            padding: 15px 20px;
            border-radius: 6px;
            margin-bottom: 20px;
            border-left: 4px solid;
        }}
        
        .alert.danger {{
            background: #fef5f5;
            border-color: #e74c3c;
            color: #991b1b;
        }}
        
        .alert.success {{
            background: #f0fdf4;
            border-color: #27ae60;
            color: #166534;
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1>📊 Attachment Architect - Visual Analysis</h1>
            <div style="color: #7f8c8d; font-size: 14px;">
                Scan ID: {scan_state['scan_id']} | 
                Completed: {datetime.fromisoformat(scan_state['completion_time']).strftime('%Y-%m-%d %H:%M:%S')} | 
                Duration: {scan_state['duration_ms']/1000:.1f}s
            </div>
        </div>
        
        <!-- Key Metrics -->
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-label">Total Storage</div>
                <div class="metric-value">{format_bytes(total_storage)}</div>
                <div class="metric-subtitle">Across all projects</div>
            </div>
            
            <div class="metric-card">
                <div class="metric-label">Total Files</div>
                <div class="metric-value">{total_files:,}</div>
                <div class="metric-subtitle">Attachments scanned</div>
            </div>
            
            <div class="metric-card">
                <div class="metric-label">Projects</div>
                <div class="metric-value">{len(projects_data)}</div>
                <div class="metric-subtitle">Active projects</div>
            </div>
            
            <div class="metric-card">
                <div class="metric-label">Avg File Size</div>
                <div class="metric-value">{format_bytes(total_storage / total_files if total_files > 0 else 0)}</div>
                <div class="metric-subtitle">Per attachment</div>
            </div>
        </div>
        
        <!-- Visual Analysis Section -->
        <div class="section">
            <div class="section-title">📈 Visual Analysis</div>
            <div class="section-subtitle">Explore attachment storage across different dimensions</div>
            
            <div class="tabs">
                <button class="tab active" onclick="showTab('projects')">📊 By Project</button>
                <button class="tab" onclick="showTab('filetypes')">🔍 By File Type</button>
                <button class="tab" onclick="showTab('users')">👥 By User</button>
                <button class="tab" onclick="showTab('age')">📅 By Age</button>
                <button class="tab" onclick="showTab('status')">📋 By Status</button>
                <button class="tab" onclick="showTab('heatindex')">🔥 Heat Index</button>
            </div>
            
            {generate_all_tabs_html(projects_data, top_file_types, top_storage_users, age_stats, status_stats, frozen_dinosaurs, heat_files)}
        </div>
    </div>
    
    <script>
        // Data
        const projectsData = {projects_json};
        const fileTypesData = {file_types_json};
        const ageData = {age_stats_json};
        const statusData = {status_stats_json};
        
        // Tab switching
        function showTab(tabName) {{
            document.querySelectorAll('.tab-content').forEach(tab => {{
                tab.style.display = 'none';
            }});
            document.querySelectorAll('.tab').forEach(tab => {{
                tab.classList.remove('active');
            }});
            
            document.getElementById(tabName).style.display = 'block';
            event.target.classList.add('active');
        }}
        
        // Format bytes
        function formatBytes(bytes) {{
            const units = ['B', 'KB', 'MB', 'GB', 'TB'];
            let value = bytes;
            let unitIndex = 0;
            
            while (value >= 1024 && unitIndex < units.length - 1) {{
                value /= 1024;
                unitIndex++;
            }}
            
            return value.toFixed(2) + ' ' + units[unitIndex];
        }}
    </script>
</body>
</html>
"""


def generate_all_tabs_html(projects_data, top_file_types, top_storage_users, age_stats, status_stats, frozen_dinosaurs, heat_files):
    """Generate all tab content HTML."""
    
    # By Project Tab
    project_html = """
            <div id="projects" class="tab-content active">
                <h3 style="margin-bottom: 10px;">Storage by Project</h3>
                <p style="color: #7f8c8d; margin-bottom: 20px;">Discover which projects consume the most storage</p>
                
                <div class="bar-chart">
    """
    
    max_size = max([p['size'] for p in projects_data]) if projects_data else 1
    for project in projects_data[:15]:
        width_pct = (project['size'] / max_size) * 100
        project_html += f"""
                    <div class="bar-item">
                        <div class="bar-label">{project['name']}</div>
                        <div class="bar-track">
                            <div class="bar-fill" style="width: {width_pct}%; background: {project['size_color']};">
                                {project['file_count']:,} files
                            </div>
                        </div>
                        <div class="bar-value">{format_bytes(project['size'])}</div>
                    </div>
        """
    
    project_html += """
                </div>
                
                <div class="pro-tip">
                    <span class="pro-tip-icon">💡 Pro Tip:</span>
                    <span class="pro-tip-text">
                        <strong>Darker blue projects</strong> have larger average file sizes. Consider if these files need compression or archival.
                    </span>
                </div>
            </div>
    """
    
    # By File Type Tab
    filetype_html = """
            <div id="filetypes" class="tab-content">
                <h3 style="margin-bottom: 10px;">File Type Analysis</h3>
                <p style="color: #7f8c8d; margin-bottom: 20px;">Discover which file types consume the most storage</p>
                
                <div class="bar-chart">
    """
    
    max_size = max([f['total_size'] for f in top_file_types]) if top_file_types else 1
    for ftype in top_file_types:
        width_pct = (ftype['total_size'] / max_size) * 100
        filetype_html += f"""
                    <div class="bar-item">
                        <div class="bar-label">.{ftype['ext']}</div>
                        <div class="bar-track">
                            <div class="bar-fill" style="width: {width_pct}%; background: {ftype['color']};">
                                {ftype['count']:,} files
                            </div>
                        </div>
                        <div class="bar-value">{format_bytes(ftype['total_size'])}</div>
                    </div>
        """
    
    filetype_html += """
                </div>
            </div>
    """
    
    # By User Tab
    user_html = """
            <div id="users" class="tab-content">
                <h3 style="margin-bottom: 10px;">User Behavior Analysis</h3>
                <p style="color: #7f8c8d; margin-bottom: 20px;">Discover which users contribute most to storage usage</p>
                
                <h4 style="margin: 30px 0 15px 0;">Top 10 Storage Consumers</h4>
                <div class="bar-chart">
    """
    
    max_size = max([u['total_storage'] for u in top_storage_users]) if top_storage_users else 1
    for user in top_storage_users:
        width_pct = (user['total_storage'] / max_size) * 100
        user_html += f"""
                    <div class="bar-item">
                        <div class="bar-label">{user['display_name']}</div>
                        <div class="bar-track">
                            <div class="bar-fill" style="width: {width_pct}%;">
                                {user['file_count']:,} files
                            </div>
                        </div>
                        <div class="bar-value">{format_bytes(user['total_storage'])}</div>
                    </div>
        """
    
    user_html += """
                </div>
            </div>
    """
    
    # By Age Tab
    age_html = """
            <div id="age" class="tab-content">
                <h3 style="margin-bottom: 10px;">Attachment Age Distribution</h3>
                <p style="color: #7f8c8d; margin-bottom: 20px;">Understand if your storage is consumed by recent or old files</p>
                
                <div class="bar-chart">
    """
    
    age_order = ['0-90 days', '90-365 days', '1-2 years', '2-4 years', '>4 years']
    max_size = max([age_stats[bucket]['total_size'] for bucket in age_order]) if age_stats else 1
    
    for bucket in age_order:
        data = age_stats[bucket]
        width_pct = (data['total_size'] / max_size) * 100 if max_size > 0 else 0
        age_html += f"""
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
    
    age_html += """
                </div>
                
                <div class="pro-tip">
                    <span class="pro-tip-icon">💡 Pro Tip:</span>
                    <span class="pro-tip-text">
                        A large amount of storage in the older categories indicates that archival policies could provide significant cost savings.
                    </span>
                </div>
            </div>
    """
    
    # By Status Tab
    status_html = """
            <div id="status" class="tab-content">
                <h3 style="margin-bottom: 10px;">Workflow Status Analysis</h3>
                <p style="color: #7f8c8d; margin-bottom: 20px;">See how storage is distributed across issue statuses</p>
                
                <div class="bar-chart">
    """
    
    max_size = max([s['total_size'] for s in status_stats]) if status_stats else 1
    for status in status_stats[:15]:
        width_pct = (status['total_size'] / max_size) * 100
        status_html += f"""
                    <div class="bar-item">
                        <div class="bar-label">{status['name']}</div>
                        <div class="bar-track">
                            <div class="bar-fill" style="width: {width_pct}%;">
                                {status['file_count']:,} files
                            </div>
                        </div>
                        <div class="bar-value">{format_bytes(status['total_size'])}</div>
                    </div>
        """
    
    status_html += """
                </div>
            </div>
    """
    
    # Heat Index Tab
    heat_html = """
            <div id="heatindex" class="tab-content">
                <h3 style="margin-bottom: 10px;">🔥 Heat Index</h3>
                <p style="color: #7f8c8d; margin-bottom: 20px;">Files with the biggest storage impact and lowest cleanup risk</p>
    """
    
    if frozen_dinosaurs:
        heat_html += f"""
                <div class="alert danger">
                    <strong>⚠️ Action Required: "Frozen Dinosaurs" Found</strong><br>
                    {len(frozen_dinosaurs)} large files (>10 MB) attached to issues inactive for over 1 year. These are prime candidates for archival.
                </div>
                
                <h4 style="margin: 20px 0 15px 0;">Top Priority Files</h4>
                <table>
                    <thead>
                        <tr>
                            <th>File Name</th>
                            <th>Size</th>
                            <th>Issue</th>
                            <th>Days Since Activity</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
        """
        
        for file in frozen_dinosaurs[:10]:
            heat_html += f"""
                        <tr>
                            <td>{file['file_name']}</td>
                            <td><strong>{format_bytes(file['file_size'])}</strong></td>
                            <td>{file['issue_key']}</td>
                            <td>{file['days_since_activity']} days</td>
                            <td>{file['status']}</td>
                        </tr>
            """
        
        heat_html += """
                    </tbody>
                </table>
        """
    else:
        heat_html += """
                <div class="alert success">
                    <strong>✅ No "Frozen Dinosaurs" Found!</strong><br>
                    Your instance doesn't have large files on inactive issues. Excellent file management!
                </div>
        """
    
    heat_html += """
            </div>
    """
    
    return project_html + filetype_html + user_html + age_html + status_html + heat_html


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python generate_visual_analysis_report.py <scan_result.json> [output.html]")
        print("\nExample:")
        print("  python generate_visual_analysis_report.py scan_9f7629d1.json report.html")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else input_file.replace('.json', '_visual_analysis.html')
    
    # Load scan data
    print(f"Loading scan data from: {input_file}")
    with open(input_file, 'r', encoding='utf-8') as f:
        scan_data = json.load(f)
    
    # Generate report
    print(f"Generating visual analysis report...")
    generate_report(scan_data, output_file)
    
    print(f"\n✅ Visual analysis report ready! Open in browser:")
    print(f"   {Path(output_file).absolute()}")


if __name__ == '__main__':
    main()
