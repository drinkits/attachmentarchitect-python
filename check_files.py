import json

with open('scan_9f7629d1.json', 'r') as f:
    data = json.load(f)

groups = list(data['duplicate_groups'].values())

# Check file sizes
large_files = [g for g in groups if g['file_size'] > 5*1024*1024]
print(f"Files > 5MB: {len(large_files)}")

# Show size distribution
sizes_mb = sorted([g['file_size']/(1024*1024) for g in groups], reverse=True)
print(f"\nTop 10 file sizes:")
for i, size in enumerate(sizes_mb[:10], 1):
    print(f"  {i}. {size:.2f} MB")

print(f"\nTotal files: {len(groups)}")
print(f"Largest file: {sizes_mb[0]:.2f} MB")
print(f"Smallest file: {sizes_mb[-1]:.4f} MB")
