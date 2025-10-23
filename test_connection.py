#!/usr/bin/env python3
"""
Test script to verify Jira Data Center connection and credentials.
"""

import os
import sys
from dotenv import load_dotenv
import requests
from requests.auth import HTTPBasicAuth


def test_connection():
    """Test connection to Jira Data Center."""
    print("="*70)
    print("Jira Data Center Connection Test")
    print("="*70)
    print()
    
    # Load environment variables
    load_dotenv()
    
    base_url = os.getenv('JIRA_BASE_URL')
    token = os.getenv('JIRA_TOKEN')
    username = os.getenv('JIRA_USERNAME')
    password = os.getenv('JIRA_PASSWORD')
    
    # Validate configuration
    if not base_url:
        print("❌ ERROR: JIRA_BASE_URL not set in .env file")
        return False
    
    if not token and not (username and password):
        print("❌ ERROR: Either JIRA_TOKEN or JIRA_USERNAME+JIRA_PASSWORD must be set")
        return False
    
    print(f"Testing connection to: {base_url}")
    print()
    
    # Create session
    session = requests.Session()
    
    # Configure authentication
    if token:
        print("Using Personal Access Token authentication")
        session.headers.update({
            'Authorization': f'Bearer {token}'
        })
    else:
        print("Using Basic Authentication")
        session.auth = HTTPBasicAuth(username, password)
    
    session.headers.update({
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    })
    
    try:
        # Test 1: Get current user
        print("\n[Test 1] Getting current user information...")
        response = session.get(f"{base_url}/rest/api/2/myself")
        response.raise_for_status()
        user_data = response.json()
        
        print(f"✓ Connected successfully!")
        print(f"  User: {user_data.get('displayName', 'Unknown')}")
        print(f"  Email: {user_data.get('emailAddress', 'N/A')}")
        print(f"  Active: {user_data.get('active', False)}")
        
        # Test 2: Get server info
        print("\n[Test 2] Getting server information...")
        response = session.get(f"{base_url}/rest/api/2/serverInfo")
        response.raise_for_status()
        server_data = response.json()
        
        print(f"✓ Server information retrieved!")
        print(f"  Version: {server_data.get('version', 'Unknown')}")
        print(f"  Build: {server_data.get('buildNumber', 'Unknown')}")
        print(f"  Server Title: {server_data.get('serverTitle', 'Unknown')}")
        
        # Test 3: Test search API
        print("\n[Test 3] Testing search API...")
        response = session.get(
            f"{base_url}/rest/api/2/search",
            params={
                'jql': 'created >= -7d',
                'maxResults': 1,
                'fields': 'key'
            }
        )
        response.raise_for_status()
        search_data = response.json()
        
        total_issues = search_data.get('total', 0)
        print(f"✓ Search API working!")
        print(f"  Issues found (last 7 days): {total_issues:,}")
        
        # Test 4: Check permissions
        print("\n[Test 4] Checking permissions...")
        response = session.get(f"{base_url}/rest/api/2/mypermissions")
        response.raise_for_status()
        perms_data = response.json()
        
        permissions = perms_data.get('permissions', {})
        browse_projects = permissions.get('BROWSE_PROJECTS', {}).get('havePermission', False)
        
        if browse_projects:
            print(f"✓ Browse Projects permission: Yes")
        else:
            print(f"⚠ Browse Projects permission: No (may limit scan scope)")
        
        # Summary
        print("\n" + "="*70)
        print("✓ All tests passed! Ready to scan.")
        print("="*70)
        print()
        print("Next step: Run the scanner")
        print("  python jira_dc_scanner.py")
        print()
        
        return True
        
    except requests.exceptions.HTTPError as e:
        print(f"\n❌ HTTP Error: {e}")
        if e.response.status_code == 401:
            print("   Authentication failed. Check your credentials.")
        elif e.response.status_code == 403:
            print("   Permission denied. Check API token permissions.")
        elif e.response.status_code == 404:
            print("   Endpoint not found. Check JIRA_BASE_URL.")
        else:
            print(f"   Status code: {e.response.status_code}")
        return False
        
    except requests.exceptions.ConnectionError:
        print(f"\n❌ Connection Error")
        print("   Cannot connect to Jira server. Check:")
        print("   - JIRA_BASE_URL is correct")
        print("   - Network connectivity")
        print("   - Firewall settings")
        return False
        
    except Exception as e:
        print(f"\n❌ Unexpected Error: {e}")
        return False


if __name__ == '__main__':
    success = test_connection()
    sys.exit(0 if success else 1)
