# 🔍 Custom JQL Query Examples

The Jira Data Center Attachment Analysis Tool supports custom JQL queries to give you complete control over which issues are scanned.

## How to Use Custom JQL

### Method 1: config.yaml (Recommended)

Edit `config.yaml` and set the `custom_jql` field:

```yaml
filters:
  custom_jql: "project = MYPROJ AND created >= -30d"
```

### Method 2: Environment Variable

Set the `CUSTOM_JQL` environment variable in your `.env` file:

```env
CUSTOM_JQL=project = MYPROJ AND created >= -30d
```

### Priority

If `custom_jql` is set, it **overrides all other filters** (projects, date_from, date_to, etc.).

---

## Common JQL Examples

### 1. Scan Specific Project

```jql
project = MYPROJECT
```

### 2. Scan Multiple Projects

```jql
project in (PROJ1, PROJ2, PROJ3)
```

### 3. Scan Recent Issues (Last 30 Days)

```jql
created >= -30d
```

### 4. Scan Date Range

```jql
created >= "2024-01-01" AND created <= "2024-12-31"
```

### 5. Scan Specific Issue Types

```jql
project = MYPROJ AND issuetype in (Bug, Task)
```

### 6. Scan by Status

```jql
project = MYPROJ AND status in ("In Progress", "To Do")
```

### 7. Scan Closed Issues Only

```jql
project = MYPROJ AND status = Done
```

### 8. Scan by Priority

```jql
project = MYPROJ AND priority in (High, Critical)
```

### 9. Scan by Assignee

```jql
project = MYPROJ AND assignee = john.doe
```

### 10. Scan Unassigned Issues

```jql
project = MYPROJ AND assignee is EMPTY
```

### 11. Scan by Reporter

```jql
project = MYPROJ AND reporter = jane.smith
```

### 12. Scan by Component

```jql
project = MYPROJ AND component = "Backend"
```

### 13. Scan by Label

```jql
project = MYPROJ AND labels = "migration"
```

### 14. Scan Issues with Attachments Only

```jql
project = MYPROJ AND attachments is not EMPTY
```

### 15. Scan Large Issues (Many Attachments)

```jql
project = MYPROJ AND attachments > 5
```

---

## Advanced Examples

### Scan Multiple Projects, Recent Issues, Specific Status

```jql
project in (PROJ1, PROJ2) AND created >= -90d AND status != Done
```

### Scan High Priority Bugs with Attachments

```jql
project = MYPROJ AND issuetype = Bug AND priority = High AND attachments is not EMPTY
```

### Scan Issues Updated Recently

```jql
project = MYPROJ AND updated >= -7d
```

### Scan Issues by Sprint

```jql
project = MYPROJ AND sprint = "Sprint 23"
```

### Scan Issues by Epic

```jql
project = MYPROJ AND "Epic Link" = PROJ-123
```

### Scan Issues by Custom Field

```jql
project = MYPROJ AND "Custom Field Name" = "Value"
```

### Exclude Specific Issue Types

```jql
project = MYPROJ AND issuetype NOT IN (Epic, Sub-task)
```

### Scan Archived Projects

```jql
project = ARCHIVED_PROJ AND created >= -365d
```

---

## Performance Tips

### 1. Use Indexed Fields

JQL queries on indexed fields are faster:
- `project`
- `issuetype`
- `status`
- `priority`
- `created`
- `updated`

### 2. Limit Date Range

Narrow date ranges improve performance:

```jql
# Good - specific range
created >= "2024-01-01" AND created <= "2024-12-31"

# Better - recent only
created >= -30d
```

### 3. Use Project Filter

Always include a project filter when possible:

```jql
# Good
project = MYPROJ AND created >= -30d

# Avoid (scans entire instance)
created >= -30d
```

### 4. Filter by Attachments

If you only care about issues with attachments:

```jql
project = MYPROJ AND attachments is not EMPTY
```

This can significantly reduce scan time.

---

## Testing Your JQL

Before running a full scan, test your JQL in Jira:

1. Go to **Issues** → **Search for Issues**
2. Click **Advanced** (top right)
3. Enter your JQL query
4. Verify the results match your expectations
5. Note the issue count (shown at top)

---

## ORDER BY Clause

The scanner automatically adds `ORDER BY created DESC` if not present. This ensures consistent pagination.

If you want a different order, specify it explicitly:

```jql
project = MYPROJ ORDER BY updated DESC
```

---

## Configuration Examples

### Example 1: Scan Single Project (Last 30 Days)

**config.yaml:**
```yaml
filters:
  custom_jql: "project = MYPROJ AND created >= -30d"
```

### Example 2: Scan Multiple Projects (Specific Date Range)

**config.yaml:**
```yaml
filters:
  custom_jql: "project in (PROJ1, PROJ2, PROJ3) AND created >= '2024-01-01' AND created <= '2024-12-31'"
```

### Example 3: Scan High Priority Issues Only

**config.yaml:**
```yaml
filters:
  custom_jql: "project = MYPROJ AND priority in (High, Critical) AND attachments is not EMPTY"
```

### Example 4: Scan Closed Issues for Cleanup

**config.yaml:**
```yaml
filters:
  custom_jql: "project = MYPROJ AND status = Done AND created <= -365d"
```

### Example 5: Scan Specific Epic

**config.yaml:**
```yaml
filters:
  custom_jql: "project = MYPROJ AND 'Epic Link' = PROJ-123"
```

---

## Fallback to Standard Filters

If `custom_jql` is **not set** (or set to `null`), the scanner uses standard filters:

**config.yaml:**
```yaml
filters:
  custom_jql: null  # Not using custom JQL
  
  # Standard filters (used instead)
  projects: ["PROJ1", "PROJ2"]
  date_from: "2024-01-01"
  date_to: "2024-12-31"
```

This is equivalent to:
```jql
project in (PROJ1, PROJ2) AND created >= '2024-01-01' AND created <= '2024-12-31' ORDER BY created DESC
```

---

## Troubleshooting

### "JQL query is invalid"

- Test your JQL in Jira's issue search first
- Check for typos in field names
- Ensure quotes around values with spaces
- Verify custom field names are correct

### "No issues found"

- Verify your JQL returns results in Jira
- Check date ranges are correct
- Ensure project keys are valid
- Confirm you have permission to view the issues

### Scan is slow

- Add `attachments is not EMPTY` to skip issues without attachments
- Narrow date range
- Limit to specific projects
- Use indexed fields in your query

---

## JQL Reference

For complete JQL documentation, see:
- [Atlassian JQL Documentation](https://support.atlassian.com/jira-service-management-cloud/docs/use-advanced-search-with-jira-query-language-jql/)
- [JQL Functions Reference](https://support.atlassian.com/jira-software-cloud/docs/jql-functions/)
- [JQL Operators Reference](https://support.atlassian.com/jira-software-cloud/docs/jql-operators/)

---

## Examples by Use Case

### Pre-Migration Audit

Scan everything before migrating to Cloud:

```jql
created >= -7300d ORDER BY created DESC
```

### Cleanup Old Closed Issues

Find duplicates in old closed issues:

```jql
project = MYPROJ AND status = Done AND created <= -365d
```

### Active Projects Only

Scan only active projects:

```jql
project in (ACTIVE1, ACTIVE2, ACTIVE3) AND status != Done
```

### Specific Team's Issues

Scan issues assigned to a specific team:

```jql
project = MYPROJ AND assignee in (user1, user2, user3)
```

### High-Value Cleanup

Focus on issues with many attachments:

```jql
project = MYPROJ AND attachments > 10
```

---

**Need help?** Check the [README.md](README.md) for more information or contact support.
