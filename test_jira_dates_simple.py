#!/usr/bin/env python3
"""
Test script to check what dates Jira API returns
Run with: python test_jira_dates_simple.py
"""

import requests
from requests.auth import HTTPBasicAuth
import json

# CONFIGURE THESE:
base_url = "YOUR_JIRA_URL"  # e.g., "https://jira.company.com"
username = "YOUR_USERNAME"
password = "YOUR_PASSWORD"
# OR use token:
token = None  # "YOUR_TOKEN"

print(f"Testing Jira API: {base_url}")
print("="*70)

# Create session
session = requests.Session()

# Configure auth
if token:
    session.headers.update({'Authorization': f'Bearer {token}'})
    print("Using: Personal Access Token")
elif username and password:
    session.auth = HTTPBasicAuth(username, password)
    print(f"Using: Basic Auth ({username})")
else:
    print("ERROR: Configure credentials in the script!")
    exit(1)

session.headers.update({
    'Accept': 'application/json',
    'Content-Type': 'application/json'
})

# Test API call
print("\nFetching first 5 issues with attachments...")
print("="*70)

jql = "project in (EK, BIS) ORDER BY created DESC"
url = f"{base_url}/rest/api/2/search"

params = {
    'jql': jql,
    'maxResults': 5,
    'fields': 'key,summary,created,updated,attachment,project,status'
}

try:
    response = session.get(url, params=params, verify=True)
    response.raise_for_status()
    data = response.json()
    
    issues = data.get('issues', [])
    print(f"Found {len(issues)} issues\n")
    
    for issue in issues:
        key = issue['key']
        fields = issue['fields']
        
        print(f"Issue: {key}")
        print(f"  Summary: {fields.get('summary', 'N/A')[:50]}")
        print(f"  Created: {fields.get('created', 'N/A')}")
        print(f"  Updated: {fields.get('updated', 'N/A')}")
        print(f"  Status: {fields.get('status', {}).get('name', 'N/A')}")
        
        attachments = fields.get('attachment', [])
        print(f"  Attachments: {len(attachments)}")
        
        if attachments:
            for att in attachments[:2]:  # Show first 2
                print(f"    - {att.get('filename')} ({att.get('size')} bytes)")
                print(f"      Created: {att.get('created')}")
        
        print()
    
    # Show raw JSON for first issue
    if issues:
        print("="*70)
        print("RAW JSON for first issue (updated field):")
        print("="*70)
        first_issue = issues[0]
        print(f"Issue Key: {first_issue['key']}")
        print(f"Updated field: {first_issue['fields'].get('updated')}")
        print(f"\nFull fields JSON:")
        print(json.dumps(first_issue['fields'], indent=2))
    
except requests.exceptions.HTTPError as e:
    print(f"HTTP Error: {e}")
    if hasattr(e, 'response'):
        print(f"Response: {e.response.text}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
