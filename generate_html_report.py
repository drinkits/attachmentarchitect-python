#!/usr/bin/env python3
"""
Generate HTML Report from Scan Results
Creates a beautiful HTML report matching Attachment Architect design
"""

import json
import sys
from datetime import datetime
from pathlib import Path


def format_bytes(bytes_value):
    """Format bytes as human-readable string."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.2f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.2f} PB"


def calculate_waste_percentage(duplicate_size, total_size):
    """Calculate waste percentage."""
    if total_size == 0:
        return 0
    return (duplicate_size / total_size) * 100


def get_health_status(waste_pct):
    """Get health status based on waste percentage."""
    if waste_pct < 10:
        return "Healthy", "green"
    elif waste_pct < 30:
        return "Warning", "orange"
    else:
        return "Critical", "red"


def generate_html_report(scan_data, output_path):
    """Generate HTML report from scan data."""
    
    scan_state = scan_data['scan_state']
    scan_stats = scan_data['scan_stats']
    duplicate_groups = scan_data['duplicate_groups']
    quick_wins = scan_data.get('quick_wins', [])
    
    # Calculate metrics
    total_storage = scan_stats['total_size']
    duplicate_storage = scan_stats['duplicate_size']
    total_files = scan_stats['total_files']
    canonical_files = scan_stats['canonical_files']
    duplicate_files = scan_stats['duplicate_files']
    waste_pct = calculate_waste_percentage(duplicate_storage, total_storage)
    health_status, health_color = get_health_status(waste_pct)
    
    # Project stats
    project_stats = scan_stats.get('project_stats', {})
    
    # File type stats
    file_type_stats = scan_stats.get('file_type_stats', {})
    
    # Sort file types by size
    sorted_file_types = sorted(
        file_type_stats.items(),
        key=lambda x: x[1]['total_size'],
        reverse=True
    )[:10]  # Top 10
    
    # Generate HTML
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Attachment Architect - Scan Report</title>
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
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
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
        
        .header .subtitle {{
            color: #7f8c8d;
            font-size: 14px;
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
        
        .metric-card.health {{
            border-left: 4px solid #3498db;
        }}
        
        .metric-card.health.green {{
            border-left-color: #27ae60;
        }}
        
        .metric-card.health.orange {{
            border-left-color: #f39c12;
        }}
        
        .metric-card.health.red {{
            border-left-color: #e74c3c;
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
        
        .metric-value.green {{
            color: #27ae60;
        }}
        
        .metric-value.orange {{
            color: #f39c12;
        }}
        
        .metric-value.red {{
            color: #e74c3c;
        }}
        
        .metric-subtitle {{
            font-size: 13px;
            color: #95a5a6;
        }}
        
        .health-bar {{
            height: 8px;
            background: #ecf0f1;
            border-radius: 4px;
            margin-top: 10px;
            overflow: hidden;
        }}
        
        .health-bar-fill {{
            height: 100%;
            transition: width 0.3s ease;
        }}
        
        .health-bar-fill.green {{
            background: #27ae60;
        }}
        
        .health-bar-fill.orange {{
            background: #f39c12;
        }}
        
        .health-bar-fill.red {{
            background: #e74c3c;
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
        }}
        
        .tab {{
            padding: 12px 24px;
            cursor: pointer;
            border-bottom: 3px solid transparent;
            margin-bottom: -2px;
            color: #7f8c8d;
            font-weight: 500;
            transition: all 0.3s;
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
        
        .project-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 15px;
        }}
        
        .project-card {{
            padding: 20px;
            border-radius: 6px;
            border: 2px solid #ecf0f1;
            transition: all 0.3s;
        }}
        
        .project-card:hover {{
            border-color: #3498db;
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }}
        
        .project-card.critical {{
            border-color: #e74c3c;
            background: #fef5f5;
        }}
        
        .project-card.warning {{
            border-color: #f39c12;
            background: #fef9f3;
        }}
        
        .project-card.healthy {{
            border-color: #27ae60;
            background: #f0fdf4;
        }}
        
        .project-name {{
            font-weight: 600;
            font-size: 16px;
            margin-bottom: 10px;
            color: #2c3e50;
        }}
        
        .project-stats {{
            font-size: 13px;
            color: #7f8c8d;
        }}
        
        .project-waste {{
            font-size: 24px;
            font-weight: 700;
            margin-top: 10px;
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
        
        .file-name {{
            font-weight: 500;
            color: #2c3e50;
        }}
        
        .file-size {{
            color: #7f8c8d;
            font-size: 14px;
        }}
        
        .duplicate-count {{
            background: #e74c3c;
            color: white;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 600;
        }}
        
        .alert {{
            padding: 15px 20px;
            border-radius: 6px;
            margin-bottom: 20px;
            border-left: 4px solid;
        }}
        
        .alert.info {{
            background: #e3f2fd;
            border-color: #2196f3;
            color: #1565c0;
        }}
        
        .alert.success {{
            background: #f0fdf4;
            border-color: #27ae60;
            color: #166534;
        }}
        
        .alert.warning {{
            background: #fef9f3;
            border-color: #f39c12;
            color: #92400e;
        }}
        
        .alert.danger {{
            background: #fef5f5;
            border-color: #e74c3c;
            color: #991b1b;
        }}
        
        .chart-container {{
            margin: 30px 0;
        }}
        
        .bar-chart {{
            display: flex;
            flex-direction: column;
            gap: 15px;
        }}
        
        .bar-item {{
            display: flex;
            align-items: center;
            gap: 15px;
        }}
        
        .bar-label {{
            min-width: 100px;
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
            position: relative;
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
            min-width: 80px;
            text-align: right;
            font-size: 14px;
            font-weight: 600;
            color: #2c3e50;
        }}
        
        .footer {{
            text-align: center;
            padding: 30px;
            color: #7f8c8d;
            font-size: 13px;
        }}
        
        .badge {{
            display: inline-block;
            padding: 4px 10px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
        }}
        
        .badge.success {{
            background: #d4edda;
            color: #155724;
        }}
        
        .badge.warning {{
            background: #fff3cd;
            color: #856404;
        }}
        
        .badge.danger {{
            background: #f8d7da;
            color: #721c24;
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1>📊 Attachment Architect</h1>
            <div class="subtitle">
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
                <div class="metric-subtitle">From {total_files:,} files</div>
            </div>
            
            <div class="metric-card">
                <div class="metric-label">Wasted on Duplicates</div>
                <div class="metric-value">{format_bytes(duplicate_storage)}</div>
                <div class="metric-subtitle">From {duplicate_files:,} duplicate copies</div>
            </div>
            
            <div class="metric-card health {health_color}">
                <div class="metric-label">Instance Health</div>
                <div class="metric-value {health_color}">{waste_pct:.0f}%</div>
                <div class="metric-subtitle">{health_status}</div>
                <div class="health-bar">
                    <div class="health-bar-fill {health_color}" style="width: {min(waste_pct, 100)}%"></div>
                </div>
            </div>
            
            <div class="metric-card">
                <div class="metric-label">Unique Files</div>
                <div class="metric-value">{canonical_files:,}</div>
                <div class="metric-subtitle">{total_files:,} total files scanned</div>
            </div>
        </div>
        
        <!-- Health Alert -->
        """
    
    if waste_pct >= 30:
        html += f"""
        <div class="alert danger">
            <strong>⚠️ Critical Storage Waste Detected</strong><br>
            {waste_pct:.1f}% of your storage is wasted on duplicate files. Immediate cleanup recommended to reclaim {format_bytes(duplicate_storage)}.
        </div>
        """
    elif waste_pct >= 10:
        html += f"""
        <div class="alert warning">
            <strong>⚡ Storage Optimization Opportunity</strong><br>
            {waste_pct:.1f}% of your storage could be reclaimed by removing {duplicate_files:,} duplicate files ({format_bytes(duplicate_storage)}).
        </div>
        """
    else:
        html += f"""
        <div class="alert success">
            <strong>✅ Healthy Storage Distribution</strong><br>
            Your instance has minimal duplicate files ({waste_pct:.1f}% waste). Keep up the good file management practices!
        </div>
        """
    
    html += """
        <!-- Visual Analysis Section -->
        <div class="section">
            <div class="section-title">📈 Visual Analysis</div>
            <div class="section-subtitle">Explore attachment storage across different dimensions</div>
            
            <div class="tabs">
                <div class="tab active" onclick="showTab('projects')">📊 By Project</div>
                <div class="tab" onclick="showTab('filetypes')">🔍 By File Type</div>
                <div class="tab" onclick="showTab('quickwins')">🎯 Quick Wins</div>
            </div>
            
            <!-- By Project Tab -->
            <div id="projects" class="tab-content active">
                <h3 style="margin-bottom: 20px;">Storage by Project</h3>
                <div class="project-grid">
    """
    
    # Project cards
    for project_key, stats in sorted(project_stats.items(), key=lambda x: x[1]['total_size'], reverse=True):
        project_waste_pct = calculate_waste_percentage(stats['duplicate_size'], stats['total_size'])
        if project_waste_pct >= 30:
            card_class = "critical"
        elif project_waste_pct >= 10:
            card_class = "warning"
        else:
            card_class = "healthy"
        
        html += f"""
                    <div class="project-card {card_class}">
                        <div class="project-name">{project_key}</div>
                        <div class="project-stats">
                            {stats['file_count']:,} files<br>
                            {format_bytes(stats['total_size'])}
                        </div>
                        <div class="project-waste" style="color: {'#e74c3c' if project_waste_pct >= 30 else '#f39c12' if project_waste_pct >= 10 else '#27ae60'}">
                            {project_waste_pct:.0f}% waste
                        </div>
                    </div>
        """
    
    html += """
                </div>
            </div>
            
            <!-- By File Type Tab -->
            <div id="filetypes" class="tab-content">
                <h3 style="margin-bottom: 20px;">File Type Analysis</h3>
                <p style="color: #7f8c8d; margin-bottom: 20px;">Discover which file types consume the most storage</p>
                <div class="bar-chart">
    """
    
    # File type bars
    max_size = max([stats['total_size'] for _, stats in sorted_file_types]) if sorted_file_types else 1
    for file_ext, stats in sorted_file_types:
        width_pct = (stats['total_size'] / max_size) * 100
        display_ext = file_ext if file_ext else "no extension"
        html += f"""
                    <div class="bar-item">
                        <div class="bar-label">.{display_ext}</div>
                        <div class="bar-track">
                            <div class="bar-fill" style="width: {width_pct}%">
                                {stats['count']:,} files
                            </div>
                        </div>
                        <div class="bar-value">{format_bytes(stats['total_size'])}</div>
                    </div>
        """
    
    html += """
                </div>
            </div>
            
            <!-- Quick Wins Tab -->
            <div id="quickwins" class="tab-content">
                <h3 style="margin-bottom: 20px;">🎯 Quick Wins - Top Duplicate Files</h3>
                <p style="color: #7f8c8d; margin-bottom: 20px;">These files have the highest impact - removing duplicates will free up the most space</p>
    """
    
    if quick_wins:
        html += """
                <table>
                    <thead>
                        <tr>
                            <th>File Name</th>
                            <th>File Size</th>
                            <th>Duplicates</th>
                            <th>Wasted Space</th>
                            <th>Impact</th>
                        </tr>
                    </thead>
                    <tbody>
        """
        
        for i, win in enumerate(quick_wins[:10], 1):
            html += f"""
                        <tr>
                            <td>
                                <div class="file-name">#{i} {win['file_name']}</div>
                            </td>
                            <td class="file-size">{format_bytes(win['file_size'])}</td>
                            <td><span class="duplicate-count">{win['duplicate_count']} copies</span></td>
                            <td><strong>{format_bytes(win['total_wasted_space'])}</strong></td>
                            <td><span class="badge danger">High Priority</span></td>
                        </tr>
            """
        
        html += """
                    </tbody>
                </table>
        """
    else:
        html += """
                <div class="alert success">
                    <strong>✅ No Duplicates Found!</strong><br>
                    Your Jira instance has no duplicate files. Excellent file management!
                </div>
        """
    
    html += """
            </div>
        </div>
        
        <!-- Scan Details -->
        <div class="section">
            <div class="section-title">📋 Scan Details</div>
            <table>
                <tr>
                    <td><strong>Scan ID</strong></td>
                    <td>{scan_id}</td>
                </tr>
                <tr>
                    <td><strong>JQL Query</strong></td>
                    <td><code>{jql_query}</code></td>
                </tr>
                <tr>
                    <td><strong>Issues Processed</strong></td>
                    <td>{processed_issues:,} / {total_issues:,}</td>
                </tr>
                <tr>
                    <td><strong>Start Time</strong></td>
                    <td>{start_time}</td>
                </tr>
                <tr>
                    <td><strong>Completion Time</strong></td>
                    <td>{completion_time}</td>
                </tr>
                <tr>
                    <td><strong>Duration</strong></td>
                    <td>{duration:.1f} seconds</td>
                </tr>
                <tr>
                    <td><strong>Status</strong></td>
                    <td><span class="badge success">{status}</span></td>
                </tr>
            </table>
        </div>
        
        <!-- Footer -->
        <div class="footer">
            Generated by <strong>Attachment Architect</strong> for Jira Data Center<br>
            Report generated on 2025-10-23 10:38:01
        </div>
    </div>
    
    <script>
        function showTab(tabName) {{
            // Hide all tabs
            document.querySelectorAll('.tab-content').forEach(tab => {{
                tab.classList.remove('active');
            }});
            document.querySelectorAll('.tab').forEach(tab => {{
                tab.classList.remove('active');
            }});
            
            // Show selected tab
            document.getElementById(tabName).classList.add('active');
            event.target.classList.add('active');
        }}
    </script>
</body>
</html>
    """.format(
        scan_id=scan_state['scan_id'],
        jql_query=scan_state.get('jql_query', 'N/A'),
        processed_issues=scan_state['processed_issues'],
        total_issues=scan_state['total_issues'],
        start_time=datetime.fromisoformat(scan_state['start_time']).strftime('%Y-%m-%d %H:%M:%S'),
        completion_time=datetime.fromisoformat(scan_state['completion_time']).strftime('%Y-%m-%d %H:%M:%S'),
        duration=scan_state['duration_ms'] / 1000,
        status=scan_state['status'].upper()
    )
    
    # Write to file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✓ HTML report generated: {output_path}")
    print(f"  Total Storage: {format_bytes(total_storage)}")
    print(f"  Duplicate Storage: {format_bytes(duplicate_storage)}")
    print(f"  Waste Percentage: {waste_pct:.1f}%")
    print(f"  Health Status: {health_status}")


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python generate_html_report.py <scan_result.json> [output.html]")
        print("\nExample:")
        print("  python generate_html_report.py scan_9f7629d1.json report.html")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else input_file.replace('.json', '.html')
    
    # Load scan data
    print(f"Loading scan data from: {input_file}")
    with open(input_file, 'r', encoding='utf-8') as f:
        scan_data = json.load(f)
    
    # Generate report
    print(f"Generating HTML report...")
    generate_html_report(scan_data, output_file)
    
    print(f"\n✅ Report ready! Open in browser:")
    print(f"   {Path(output_file).absolute()}")


if __name__ == '__main__':
    main()
