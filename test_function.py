import generate_visual_analysis_report as g
import json

with open('scan_9f7629d1.json', 'r') as f:
    data = json.load(f)

result = g.calculate_heat_index(data['duplicate_groups'])
print(f"Heat files: {len(result)}")
if result:
    print(f"\nFirst 3 files:")
    for i, f in enumerate(result[:3], 1):
        print(f"  {i}. {f['file_name']} - {f['file_size']/(1024*1024):.2f} MB - {f['days_since_activity']} days")
else:
    print("No files found!")
