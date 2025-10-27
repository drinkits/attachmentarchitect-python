"""
HTML generation module for visual analysis report
"""

import json
from datetime import datetime


def format_bytes(bytes_value):
    """Format bytes as human-readable string."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.2f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.2f} PB"


def generate_html(scan_state, projects_data, top_file_types, top_storage_users,
                  age_stats, status_stats, frozen_dinosaurs, remaining_files,
                  total_storage, total_files, min_file_size_mb, min_days_inactive):
    """Generate complete HTML content."""
    
    projects_json = json.dumps(projects_data)
    file_types_json = json.dumps(top_file_types)
    age_stats_json = json.dumps(age_stats)
    status_stats_json = json.dumps(status_stats)
    remaining_files_json = json.dumps(remaining_files)
    
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
            min-width: 50px;
            max-width: 150px;
            font-size: 14px;
            font-weight: 500;
            color: #2c3e50;
            overflow: hidden;
        }}
        
        .bar-label-wide {{
            min-width: 280px;
            max-width: 350px;
            font-size: 13px;
        }}
        
        .bar-track {{
            flex: 1;
            height: 30px;
            background: #ecf0f1;
            border-radius: 4px;
            overflow: visible;
            position: relative;
        }}
        
        .bar-fill {{
            height: 100%;
            background: linear-gradient(90deg, #3498db, #2980b9);
            display: flex;
            align-items: center;
            padding: 0 10px;
            color: rgba(0, 0, 0, 0.7);
            font-size: 12px;
            font-weight: 600;
            transition: width 0.5s ease;
            white-space: nowrap;
            border-radius: 4px;
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
            cursor: pointer;
            user-select: none;
            position: relative;
        }}
        
        th:hover {{
            background: #e9ecef;
        }}
        
        th.sortable::after {{
            content: ' ⇅';
            opacity: 0.3;
            font-size: 10px;
        }}
        
        th.sort-asc::after {{
            content: ' ▲';
            opacity: 1;
        }}
        
        th.sort-desc::after {{
            content: ' ▼';
            opacity: 1;
        }}
        
        td {{
            padding: 15px 12px;
            border-bottom: 1px solid #ecf0f1;
            font-size: 14px;
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
        
        .collapsible {{
            background: #f8f9fa;
            border: 1px solid #ecf0f1;
            border-radius: 6px;
            margin-top: 30px;
            overflow: hidden;
        }}
        
        .collapsible-header {{
            padding: 15px 20px;
            cursor: pointer;
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: #f8f9fa;
            transition: background 0.3s;
        }}
        
        .collapsible-header:hover {{
            background: #ecf0f1;
        }}
        
        .collapsible-header h4 {{
            margin: 0;
            color: #2c3e50;
            font-size: 16px;
        }}
        
        .collapsible-icon {{
            font-size: 20px;
            color: #7f8c8d;
            transition: transform 0.3s;
        }}
        
        .collapsible-icon.open {{
            transform: rotate(180deg);
        }}
        
        .collapsible-content {{
            max-height: 0;
            overflow: hidden;
            transition: max-height 0.3s ease;
        }}
        
        .collapsible-content.open {{
            max-height: 2000px;
        }}
        
        .collapsible-body {{
            padding: 20px;
            background: white;
        }}
        
        .search-box {{
            margin-bottom: 20px;
        }}
        
        .search-box input {{
            width: 100%;
            padding: 10px 15px;
            border: 1px solid #ecf0f1;
            border-radius: 4px;
            font-size: 14px;
        }}
        
        .pagination {{
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 10px;
            margin-top: 20px;
        }}
        
        .pagination button {{
            padding: 8px 12px;
            border: 1px solid #ecf0f1;
            background: white;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
        }}
        
        .pagination button:hover:not(:disabled) {{
            background: #f8f9fa;
        }}
        
        .pagination button:disabled {{
            opacity: 0.5;
            cursor: not-allowed;
        }}
        
        .pagination span {{
            color: #7f8c8d;
            font-size: 14px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- Header with Branding -->
        <div class="header">
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 15px;">
                <div style="display: flex; align-items: center;">
                    <div style="font-size: 48px; margin-right: 15px;">📊</div>
                    <div>
                        <h1 style="margin: 0; font-size: 28px;">Attachment Architect</h1>
                        <div style="color: #7f8c8d; font-size: 14px; margin-top: 5px;">
                            Pre-Migration Storage Analysis Report
                        </div>
                    </div>
                </div>
                <div style="text-align: right; color: #7f8c8d; font-size: 13px;">
                    <div><strong>Scan ID:</strong> {scan_state['scan_id']}</div>
                    <div><strong>Completed:</strong> {datetime.fromisoformat(scan_state['completion_time']).strftime('%Y-%m-%d %H:%M:%S')}</div>
                    <div><strong>Duration:</strong> {scan_state['duration_ms']/1000:.1f}s</div>
                </div>
            </div>
            <div style="background: #e3f2fd; border-left: 4px solid #2196f3; padding: 12px 15px; border-radius: 4px; font-size: 14px;">
                <strong>💡 Pre-Migration Insight:</strong> This one-time analysis provides a snapshot of your Data Center storage. 
                Planning to migrate to Cloud? Consider continuous monitoring to keep your new instance clean from Day 1.
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
            
            {generate_all_tabs(projects_data, top_file_types, top_storage_users, age_stats, status_stats, frozen_dinosaurs, remaining_files, min_file_size_mb, min_days_inactive)}
        </div>
    </div>
    
    <!-- Footer with Call-to-Action -->
    <footer style="margin-top: 50px; padding: 40px 30px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        <div style="max-width: 900px; margin: 0 auto; text-align: center;">
            <h2 style="font-size: 32px; margin-bottom: 15px; color: white;">From a One-Time Snapshot to a Live Command Center</h2>
            
            <p style="font-size: 18px; line-height: 1.8; margin-bottom: 25px; opacity: 0.95;">
                This free report has given you a powerful <strong>one-time snapshot</strong> of your Data Center instance. 
                It's the perfect starting point for your cleanup and migration plan.
            </p>
            
            <p style="font-size: 16px; line-height: 1.7; margin-bottom: 30px; opacity: 0.9;">
                But what happens after you migrate to the Cloud? You need a way to <em>keep</em> it clean.
            </p>
            
            <div style="background: rgba(255,255,255,0.15); padding: 25px; border-radius: 8px; margin-bottom: 30px; backdrop-filter: blur(10px);">
                <h3 style="font-size: 24px; margin-bottom: 15px; color: white;">
                    🚀 Attachment Architect for Jira Cloud
                </h3>
                <p style="font-size: 16px; line-height: 1.7; margin-bottom: 15px;">
                    Get this same level of deep insight and much more with a <strong>live, continuous dashboard</strong>. 
                    Instead of a static report, get a real-time command center that helps you:
                </p>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 12px; text-align: left; max-width: 700px; margin: 20px auto 0; font-size: 15px;">
                    <div>📊 <strong>Visualize</strong> your entire attachment library with interactive charts</div>
                    <div>🔍 <strong>Investigate</strong> every duplicate with detailed, drill-down views</div>
                    <div>🧹 <strong>Clean Up</strong> safely with our secure, multi-step bulk deletion workflow</div>
                </div>
                <p style="font-size: 15px; margin-top: 20px; opacity: 0.95;">
                    Keep your new Cloud instance clean from Day 1.
                </p>
            </div>
            
            <div style="display: flex; gap: 15px; justify-content: center; flex-wrap: wrap; margin-bottom: 20px;">
                <a href="https://marketplace.atlassian.com/apps/2464899201/attachment-architect" 
                   style="display: inline-block; padding: 15px 35px; background-color: white; color: #667eea; text-decoration: none; border-radius: 6px; font-weight: bold; font-size: 16px; box-shadow: 0 4px 6px rgba(0,0,0,0.2); transition: transform 0.2s;"
                   onmouseover="this.style.transform='translateY(-2px)'"
                   onmouseout="this.style.transform='translateY(0)'"
                   target="_blank">
                    📦 View on Atlassian Marketplace
                </a>
            </div>
            
            <div style="font-size: 14px; opacity: 0.9; margin-top: 25px; padding-top: 25px; border-top: 1px solid rgba(255,255,255,0.3);">
                <p style="margin-bottom: 10px;">
                    <strong>Why a Live Dashboard Matters:</strong>
                </p>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; text-align: left; max-width: 800px; margin: 15px auto 0;">
                    <div>✅ <strong>Always Up-to-Date Insights</strong></div>
                    <div>✅ <strong>Interactive Data Visualization</strong></div>
                    <div>✅ <strong>Multi-Step Safe Deletion</strong></div>
                    <div>✅ <strong>Comprehensive Audit Log</strong></div>
                    <div>✅ <strong>Prioritized "Quick Wins"</strong></div>
                    <div>✅ <strong>"Frozen Dinosaur" Analysis</strong></div>
                </div>
            </div>
        </div>
    </footer>

    <!-- Branding Footer -->
    <div style="text-align: center; padding: 30px 20px; background: #f8f9fa; border-radius: 8px; margin-top: 30px;">
        <div style="max-width: 800px; margin: 0 auto;">
            <h3 style="color: #2c3e50; margin-bottom: 15px; font-size: 18px;">🚀 Want to Run Your Own Analysis?</h3>
            <p style="color: #7f8c8d; font-size: 14px; line-height: 1.6; margin-bottom: 20px;">
                This report was generated using our <strong>free Data Center scanner</strong>. 
                Download it and run your own analysis in minutes - no Python knowledge required!
            </p>
            
            <div style="background: white; padding: 20px; border-radius: 6px; margin-bottom: 20px; text-align: left; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                <h4 style="color: #2c3e50; margin-bottom: 10px; font-size: 16px;">✨ Super Easy to Use:</h4>
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px; color: #555; font-size: 13px;">
                    <div>✅ <strong>Windows:</strong> Just double-click <code style="background: #f0f0f0; padding: 2px 6px; border-radius: 3px;">setup.bat</code></div>
                    <div>✅ <strong>No coding needed:</strong> Simple BAT/SH scripts</div>
                    <div>✅ <strong>Auto-setup:</strong> Installs everything for you</div>
                    <div>✅ <strong>5-minute start:</strong> From download to first scan</div>
                </div>
            </div>
            
            <p style="color: #7f8c8d; font-size: 13px; margin-bottom: 15px;">
                Report generated by <strong>Attachment Architect</strong> | 
                <a href="https://github.com/drinkits/attachmentarchitect-python/releases" style="color: #3498db; text-decoration: none;" target="_blank">Download Scanner</a> | 
                <a href="mailto:support@drinkits.lv" style="color: #3498db; text-decoration: none;">Contact Support</a>
            </p>
            <p style="color: #95a5a6; font-size: 12px;">
                © 2025 Attachment Architect Team. All rights reserved.
            </p>
        </div>
    </div>
    
    <script>
        const projectsData = {projects_json};
        const fileTypesData = {file_types_json};
        const ageData = {age_stats_json};
        const statusData = {status_stats_json};
        const remainingFiles = {remaining_files_json};
        
        let currentPage = 1;
        const itemsPerPage = 10;
        let filteredFiles = [...remainingFiles];
        let currentSortColumn = null;
        let currentSortDirection = 'desc';
        
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
        
        function toggleCollapsible(id) {{
            const content = document.getElementById(id);
            const icon = document.getElementById(id + '-icon');
            
            if (content.classList.contains('open')) {{
                content.classList.remove('open');
                icon.classList.remove('open');
            }} else {{
                content.classList.add('open');
                icon.classList.add('open');
            }}
        }}
        
        function searchFiles() {{
            const searchTerm = document.getElementById('file-search').value.toLowerCase();
            filteredFiles = remainingFiles.filter(file => 
                file.file_name.toLowerCase().includes(searchTerm) ||
                file.issue_key.toLowerCase().includes(searchTerm) ||
                file.status.toLowerCase().includes(searchTerm)
            );
            currentPage = 1;
            renderFilesTable();
        }}
        
        function renderFilesTable() {{
            const start = (currentPage - 1) * itemsPerPage;
            const end = start + itemsPerPage;
            const pageFiles = filteredFiles.slice(start, end);
            
            const tbody = document.getElementById('remaining-files-tbody');
            tbody.innerHTML = '';
            
            pageFiles.forEach(file => {{
                const row = document.createElement('tr');
                row.innerHTML = `
                    <td>${{file.file_name}}</td>
                    <td><strong>${{formatBytes(file.file_size)}}</strong></td>
                    <td>${{file.issue_key}}</td>
                    <td>${{file.days_since_activity}} days</td>
                    <td>${{file.status}}</td>
                    <td>${{file.heat_score.toFixed(2)}}</td>
                `;
                tbody.appendChild(row);
            }});
            
            updatePagination();
        }}
        
        function updatePagination() {{
            const totalPages = Math.ceil(filteredFiles.length / itemsPerPage);
            document.getElementById('page-info').textContent = `Page ${{currentPage}} of ${{totalPages}}`;
            document.getElementById('prev-btn').disabled = currentPage === 1;
            document.getElementById('next-btn').disabled = currentPage === totalPages;
        }}
        
        function prevPage() {{
            if (currentPage > 1) {{
                currentPage--;
                renderFilesTable();
            }}
        }}
        
        function nextPage() {{
            const totalPages = Math.ceil(filteredFiles.length / itemsPerPage);
            if (currentPage < totalPages) {{
                currentPage++;
                renderFilesTable();
            }}
        }}
        
        function sortTable(columnIndex) {{
            const columnMap = {{
                0: 'file_name',
                1: 'file_size',
                2: 'issue_key',
                3: 'days_since_activity',
                4: 'status',
                5: 'heat_score'
            }};
            
            const column = columnMap[columnIndex];
            
            // Toggle sort direction if clicking same column
            if (currentSortColumn === column) {{
                currentSortDirection = currentSortDirection === 'asc' ? 'desc' : 'asc';
            }} else {{
                currentSortColumn = column;
                currentSortDirection = 'desc';
            }}
            
            // Sort the filtered files
            filteredFiles.sort((a, b) => {{
                let aVal = a[column];
                let bVal = b[column];
                
                // Handle string comparison
                if (typeof aVal === 'string') {{
                    aVal = aVal.toLowerCase();
                    bVal = bVal.toLowerCase();
                }}
                
                if (currentSortDirection === 'asc') {{
                    return aVal > bVal ? 1 : aVal < bVal ? -1 : 0;
                }} else {{
                    return aVal < bVal ? 1 : aVal > bVal ? -1 : 0;
                }}
            }});
            
            // Update header classes
            document.querySelectorAll('#remaining-files thead th').forEach((th, idx) => {{
                th.classList.remove('sort-asc', 'sort-desc');
                th.classList.add('sortable');
                if (idx === columnIndex) {{
                    th.classList.add(currentSortDirection === 'asc' ? 'sort-asc' : 'sort-desc');
                }}
            }});
            
            currentPage = 1;
            renderFilesTable();
        }}
        
        // Initialize table headers with click handlers
        function initializeSorting() {{
            const headers = document.querySelectorAll('#remaining-files thead th');
            headers.forEach((th, index) => {{
                th.classList.add('sortable');
                th.addEventListener('click', () => sortTable(index));
            }});
        }}
        
        // Initialize
        renderFilesTable();
        
        // Initialize sorting when collapsible is opened
        document.querySelector('.collapsible-header').addEventListener('click', function() {{
            setTimeout(() => {{
                if (document.getElementById('remaining-files').classList.contains('open')) {{
                    initializeSorting();
                }}
            }}, 100);
        }});
    </script>
</body>
</html>
"""


def generate_all_tabs(projects_data, top_file_types, top_storage_users, age_stats, status_stats, frozen_dinosaurs, remaining_files, min_file_size_mb, min_days_inactive):
    """Generate all tab content."""
    
    tabs_html = ""
    
    # By Project Tab
    tabs_html += generate_project_tab(projects_data)
    
    # By File Type Tab
    tabs_html += generate_filetype_tab(top_file_types)
    
    # By User Tab
    tabs_html += generate_user_tab(top_storage_users)
    
    # By Age Tab
    tabs_html += generate_age_tab(age_stats)
    
    # By Status Tab
    tabs_html += generate_status_tab(status_stats)
    
    # Heat Index Tab
    tabs_html += generate_heat_index_tab(frozen_dinosaurs, remaining_files, min_file_size_mb, min_days_inactive)
    
    return tabs_html


def generate_project_tab(projects_data):
    """Generate project tab content."""
    html = """
            <div id="projects" class="tab-content active">
                <h3 style="margin-bottom: 10px;">Storage by Project</h3>
                <p style="color: #7f8c8d; margin-bottom: 20px;">Discover which projects consume the most storage</p>
                
                <div class="bar-chart">
    """
    
    max_size = max([p['size'] for p in projects_data]) if projects_data else 1
    for project in projects_data[:15]:
        width_pct = (project['size'] / max_size) * 100
        html += f"""
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
    
    html += """
                </div>
                
                <div class="pro-tip">
                    <span class="pro-tip-icon">💡 Pro Tip:</span>
                    <span class="pro-tip-text">
                        <strong>Darker blue projects</strong> have larger average file sizes. Consider if these files need compression or archival.
                    </span>
                </div>
            </div>
    """
    
    return html


def generate_filetype_tab(top_file_types):
    """Generate file type tab content."""
    html = """
            <div id="filetypes" class="tab-content">
                <h3 style="margin-bottom: 10px;">File Type Analysis</h3>
                <p style="color: #7f8c8d; margin-bottom: 20px;">Discover which file types consume the most storage</p>
                
                <div class="bar-chart">
    """
    
    max_size = max([f['total_size'] for f in top_file_types]) if top_file_types else 1
    for ftype in top_file_types:
        width_pct = (ftype['total_size'] / max_size) * 100
        html += f"""
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
    
    html += """
                </div>
            </div>
    """
    
    return html


def generate_user_tab(top_storage_users):
    """Generate user tab content."""
    html = """
            <div id="users" class="tab-content">
                <h3 style="margin-bottom: 10px;">User Behavior Analysis</h3>
                <p style="color: #7f8c8d; margin-bottom: 20px;">Discover which users contribute most to storage usage</p>
                
                <h4 style="margin: 30px 0 15px 0;">Top 10 Storage Consumers</h4>
                <div class="bar-chart">
    """
    
    max_size = max([u['total_storage'] for u in top_storage_users]) if top_storage_users else 1
    for user in top_storage_users:
        width_pct = (user['total_storage'] / max_size) * 100
        # Format as "Name Surname (username)"
        user_label = f"{user['display_name']} ({user['user_id']})"
        html += f"""
                    <div class="bar-item">
                        <div class="bar-label bar-label-wide" title="{user_label}">{user_label}</div>
                        <div class="bar-track">
                            <div class="bar-fill" style="width: {width_pct}%;">
                                {user['file_count']:,} files
                            </div>
                        </div>
                        <div class="bar-value">{format_bytes(user['total_storage'])}</div>
                    </div>
        """
    
    html += """
                </div>
            </div>
    """
    
    return html


def generate_age_tab(age_stats):
    """Generate age tab content."""
    html = """
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


def generate_status_tab(status_stats):
    """Generate status tab content."""
    html = """
            <div id="status" class="tab-content">
                <h3 style="margin-bottom: 10px;">Workflow Status Analysis</h3>
                <p style="color: #7f8c8d; margin-bottom: 20px;">See how storage is distributed across issue statuses</p>
                
                <div class="bar-chart">
    """
    
    max_size = max([s['total_size'] for s in status_stats]) if status_stats else 1
    for status in status_stats[:15]:
        width_pct = (status['total_size'] / max_size) * 100
        # Format as "Status Name (ID: X)" if status_id is available
        status_label = status['name']
        if status.get('status_id'):
            status_label = f"{status['name']} (ID: {status['status_id']})"
        
        html += f"""
                    <div class="bar-item">
                        <div class="bar-label bar-label-wide" title="{status_label}">{status_label}</div>
                        <div class="bar-track">
                            <div class="bar-fill" style="width: {width_pct}%;">
                                {status['file_count']:,} files
                            </div>
                        </div>
                        <div class="bar-value">{format_bytes(status['total_size'])}</div>
                    </div>
        """
    
    html += """
                </div>
            </div>
    """
    
    return html


def generate_heat_index_tab(frozen_dinosaurs, remaining_files, min_file_size_mb, min_days_inactive):
    """Generate heat index tab content with two-part structure."""
    html = """
            <div id="heatindex" class="tab-content">
                <h3 style="margin-bottom: 10px;">🔥 Heat Index</h3>
                <p style="color: #7f8c8d; margin-bottom: 20px;">Files with the biggest storage impact and lowest cleanup risk</p>
    """
    
    # Part 1: Frozen Dinosaurs
    if frozen_dinosaurs:
        html += f"""
                <div class="alert danger">
                    <strong>⚠️ Action Required: "Frozen Dinosaurs" Found</strong><br>
                    {len(frozen_dinosaurs)} large files (>{min_file_size_mb} MB) attached to issues inactive for over {min_days_inactive} days. These are prime candidates for archival.
                </div>
                
                <h4 style="margin: 20px 0 15px 0;">Top Priority Files (Sorted by Heat Score)</h4>
                <table>
                    <thead>
                        <tr>
                            <th>File Name</th>
                            <th>Size</th>
                            <th>Issue</th>
                            <th>Days Since Activity</th>
                            <th>Status</th>
                            <th>Heat Score</th>
                        </tr>
                    </thead>
                    <tbody>
        """
        
        for file in frozen_dinosaurs[:10]:
            html += f"""
                        <tr>
                            <td>{file['file_name']}</td>
                            <td><strong>{format_bytes(file['file_size'])}</strong></td>
                            <td>{file['issue_key']}</td>
                            <td>{file['days_since_activity']} days</td>
                            <td>{file['status']}</td>
                            <td>{file['heat_score']:.2f}</td>
                        </tr>
            """
        
        html += """
                    </tbody>
                </table>
        """
    else:
        html += f"""
                <div class="alert success">
                    <strong>✅ No "Frozen Dinosaurs" Found!</strong><br>
                    Your instance doesn't have large files (>{min_file_size_mb} MB) on issues inactive for over {min_days_inactive} days. Excellent file management!
                </div>
        """
    
    # Part 2: Explore All Remaining Files (Collapsible)
    if remaining_files:
        html += f"""
                <div class="collapsible">
                    <div class="collapsible-header" onclick="toggleCollapsible('remaining-files')">
                        <h4>🔍 Explore All Remaining Files ({len(remaining_files)} files)</h4>
                        <span class="collapsible-icon" id="remaining-files-icon">▼</span>
                    </div>
                    <div class="collapsible-content" id="remaining-files">
                        <div class="collapsible-body">
                            <div class="search-box">
                                <input type="text" id="file-search" placeholder="Search by file name, issue key, or status..." onkeyup="searchFiles()">
                            </div>
                            
                            <table>
                                <thead>
                                    <tr>
                                        <th>File Name</th>
                                        <th>Size</th>
                                        <th>Issue</th>
                                        <th>Days Since Activity</th>
                                        <th>Status</th>
                                        <th>Heat Score</th>
                                    </tr>
                                </thead>
                                <tbody id="remaining-files-tbody">
                                </tbody>
                            </table>
                            
                            <div class="pagination">
                                <button id="prev-btn" onclick="prevPage()">Previous</button>
                                <span id="page-info"></span>
                                <button id="next-btn" onclick="nextPage()">Next</button>
                            </div>
                        </div>
                    </div>
                </div>
        """
    
    html += """
            </div>
    """
    
    return html
