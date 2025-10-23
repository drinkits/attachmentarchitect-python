# Visual Analysis Report Generator

## Features

### 📊 Six Analysis Tabs

1. **By Project** - Storage consumption by project with color-coded average file sizes
2. **By File Type** - File type analysis with color-coded bars
3. **By User** - Top 10 storage consumers
4. **By Age** - Attachment age distribution (0-90 days, 90-365 days, 1-2 years, 2-4 years, >4 years)
5. **By Status** - Workflow status analysis
6. **🔥 Heat Index** - Two-part structure:
   - **Part 1: "Frozen Dinosaurs"** - High-priority files for archival (configurable criteria)
   - **Part 2: "Explore All Remaining Files"** - Searchable, filterable, paginated table (collapsed by default)

## Usage

### Basic Usage
```bash
python generate_visual_analysis_report.py scan_9f7629d1.json
```

### Custom Output File
```bash
python generate_visual_analysis_report.py scan_9f7629d1.json my_report.html
```

### Configure "Frozen Dinosaurs" Criteria
```bash
# Files larger than 5 MB and inactive for more than 180 days
python generate_visual_analysis_report.py scan_9f7629d1.json --min-size 5 --min-days 180

# Files larger than 20 MB and inactive for more than 730 days (2 years)
python generate_visual_analysis_report.py scan_9f7629d1.json --min-size 20 --min-days 730
```

## Command-Line Arguments

- `input_file` - Input JSON scan file (required)
- `output_file` - Output HTML file (optional, defaults to `<input>_visual_analysis.html`)
- `--min-size` - Minimum file size in MB for "Frozen Dinosaurs" (default: 10)
- `--min-days` - Minimum days since last activity for "Frozen Dinosaurs" (default: 365)

## Heat Index Features

### Frozen Dinosaurs
- Automatically identifies files that meet BOTH criteria:
  - File size > `--min-size` MB
  - Days since last issue activity > `--min-days`
- Sorted by Heat Score (size × age)
- Shows top 10 priority files
- Visual alert with red background

### Explore All Remaining Files
- Collapsible section (collapsed by default)
- **Search functionality** - Filter by file name, issue key, or status
- **Pagination** - 10 items per page
- Shows all files that don't meet "Frozen Dinosaurs" criteria
- Sortable by heat score

## Output

The script generates a single HTML file with:
- ✅ Responsive design
- ✅ Interactive tabs
- ✅ Color-coded visualizations
- ✅ Pro tips for each analysis
- ✅ No external dependencies (all CSS/JS inline)

## Files

- `generate_visual_analysis_report.py` - Main script
- `generate_html_content.py` - HTML generation module
- `generate_visual_analysis_report.py.backup` - Backup of previous version

## Example Output

```
✓ Visual analysis report generated: scan_9f7629d1_visual_analysis.html
  Total Storage: 1.30 GB
  Total Files: 1,346
  Projects: 2
  File Types: 16
  Frozen Dinosaurs: 0 (>5.0MB, >180 days)
  Remaining Files: 1,346
```

Open the HTML file in any modern browser to view the interactive report!
