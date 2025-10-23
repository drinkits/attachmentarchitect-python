# Report Formatting Updates

## ✅ Changes Made

### 1. **User Display Format**
**Format**: `Name Surname (username)`

**Example**: 
- Before: `Aivars Delveris`
- After: `Aivars Delveris (adelveri)`

**Location**: "By User" tab in visual analysis report

### 2. **Status Display Format**
**Format**: `Status Name (ID: X)` *(when status ID is available)*

**Example**:
- Before: `Planned`
- After: `Planned (ID: 3)`

**Location**: "By Status" tab in visual analysis report

## 📝 Note About Status IDs

**Current Status**: The scanner does NOT currently capture status IDs from the Jira API.

**Why**: The Jira API returns status as an object with `id`, `name`, and other fields, but the scanner only extracts the `name` field.

**Impact**: Status IDs will NOT appear in reports generated from existing scans. They will show as just "Status Name" without the ID.

**To Add Status IDs**: The scanner (`jira_dc_scanner.py`) needs to be updated to capture `status.id` from the Jira API response.

## 🔧 How to Update Scanner to Capture Status IDs

In `jira_dc_scanner.py`, find the `_process_issue` method (around line 1046) and update:

```python
# Current code:
status = fields.get('status', {})
status_name = status.get('name', 'Unknown')

# Add this line:
status_id = status.get('id', None)
```

Then pass `status_id` to `_process_attachment_result` and store it in `duplicate_groups`.

## 📊 Report Generation

Generate report with:
```bash
python generate_visual_analysis_report.py scan_25ff7c46.json
```

The report will automatically:
- Show usernames as "Name (username)"
- Show status IDs as "Status (ID: X)" if available in scan data
- Gracefully handle missing status IDs (shows just status name)

## ✅ Backward Compatibility

The changes are **backward compatible**:
- Old scan data without status IDs will still work
- Reports will show "Status Name" without ID if not available
- No errors or breaking changes
