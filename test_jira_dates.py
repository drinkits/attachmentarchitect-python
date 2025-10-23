#!/usr/bin/env python3
"""
Test script to check what dates Jira API returns
"""

import requests
from requests.auth import HTTPBasicAuth
import json
import os
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Get credentials
base_url = os.getenv('JIRA_BASE_URL')
token = os.getenv('JIRA_TOKEN')
username = os.getenv('JIRA_USERNAME')
password = os.getenv('JIRA_PASSWORD')

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
    print("ERROR: No credentials found!")
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
        print(f"  Summary: {fields.get('summary', 'N/A')}")
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
        print("RAW JSON for first issue (fields only):")
        print("="*70)
        print(json.dumps(issues[0]['fields'], indent=2))
    
except requests.exceptions.HTTPError as e:
    print(f"HTTP Error: {e}")
    print(f"Response: {e.response.text}")
except Exception as e:
    print(f"Error: {e}")
