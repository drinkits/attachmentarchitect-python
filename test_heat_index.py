from datetime import datetime, timezone
import json

# Load data
with open('scan_9f7629d1.json', 'r') as f:
    data = json.load(f)

group = list(data['duplicate_groups'].values())[0]
print(f"Sample file: {group['file_name']}")
print(f"File size: {group['file_size']} bytes ({group['file_size']/(1024*1024):.2f} MB)")
print(f"Updated: {group['issue_last_updated']}")

# Parse date
updated_str = group['issue_last_updated'].replace('Z', '+00:00')
print(f"After replace Z: {updated_str}")

# Handle +0300 format
if '+' in updated_str and updated_str.count('+') == 1:
    parts = updated_str.rsplit('+', 1)
    print(f"Parts: {parts}")
    if len(parts[1]) == 4:  # +0300 format
        updated_str = parts[0] + '+' + parts[1][:2] + ':' + parts[1][2:]
        print(f"Converted to: {updated_str}")

try:
    updated = datetime.fromisoformat(updated_str)
    print(f"Parsed datetime: {updated}")
    
    now = datetime.now(timezone.utc)
    print(f"Now (UTC): {now}")
    
    diff = (now - updated).days
    print(f"Days difference: {diff}")
    print(f"Absolute days: {abs(diff)}")
    
    # Check criteria
    min_size_mb = 5
    min_days = 60
    min_size_bytes = min_size_mb * 1024 * 1024
    
    print(f"\nCriteria check:")
    print(f"  File size > {min_size_mb} MB? {group['file_size']} > {min_size_bytes} = {group['file_size'] > min_size_bytes}")
    print(f"  Days > {min_days}? {abs(diff)} > {min_days} = {abs(diff) > min_days}")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
