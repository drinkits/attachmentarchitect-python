#!/usr/bin/env python3
"""Script to fix the build_jql_query method"""

# Read the file
with open('jira_dc_scanner.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the method
start = next(i for i, line in enumerate(lines) if 'def build_jql_query' in line)
end = next(i for i in range(start+1, len(lines)) if lines[i].strip().startswith('def '))

# New method implementation
new_method = '''    def build_jql_query(self) -> str:
        """Build JQL query based on filters or custom JQL."""
        filters = self.config.get('filters', {})
        
        # Check for custom JQL first (overrides all other filters)
        custom_jql = filters.get('custom_jql')
        if custom_jql:
            self.logger.info(f"Using custom JQL query: {custom_jql}")
            # Ensure ORDER BY is present for consistent pagination
            if 'ORDER BY' not in custom_jql.upper():
                custom_jql += " ORDER BY created DESC"
            return custom_jql
        
        # Build JQL from standard filters
        jql_parts = []
        
        # Project filter
        projects = filters.get('projects', [])
        if projects:
            project_list = ', '.join(projects)
            jql_parts.append(f"project in ({project_list})")
        
        # Date range filter
        date_from = filters.get('date_from')
        if date_from:
            jql_parts.append(f"created >= '{date_from}'")
        
        date_to = filters.get('date_to')
        if date_to:
            jql_parts.append(f"created <= '{date_to}'")
        
        # Default: last 20 years if no date filter
        if not date_from and not date_to:
            jql_parts.append("created >= -7300d")
        
        # Combine with AND
        jql = ' AND '.join(jql_parts) if jql_parts else "created >= -7300d"
        jql += " ORDER BY created DESC"
        
        return jql

'''

# Replace the method
new_lines = lines[:start] + [new_method] + lines[end:]

# Write back
with open('jira_dc_scanner.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print(f"✓ Fixed build_jql_query method (lines {start+1} to {end})")
print(f"✓ Added custom_jql support")
