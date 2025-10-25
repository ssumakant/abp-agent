# Merge Instructions for v3.1.0

**Branch:** `claude/clone-abp-agent-repo-011CUTMj7L4RuoUHQpUhKFNn`
**Target:** `main`
**Date:** October 25, 2025
**Version:** v3.1.0

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Pre-Merge Checklist](#pre-merge-checklist)
3. [Merge Steps](#merge-steps)
4. [Post-Merge Verification](#post-merge-verification)
5. [Troubleshooting](#troubleshooting)
6. [Rollback Procedures](#rollback-procedures)

---

## Prerequisites

### Required Access
- ✅ Write access to the `main` branch
- ✅ Ability to push to remote repository
- ✅ Permission to merge pull requests (if using PR workflow)

### Required Tools
- ✅ Git v2.0+
- ✅ Python 3.11+
- ✅ pip package manager

### Knowledge Requirements
- ✅ Understanding of git merge/rebase workflows
- ✅ Basic FastAPI application deployment
- ✅ SQLite database concepts

---

## Pre-Merge Checklist

### ✅ Code Review
- [ ] Review all changes in `docs/v3.1.0_RELEASE_NOTES.md`
- [ ] Review `CHANGELOG.md` for v3.1.0 entry
- [ ] Verify critical bug fixes address the stated issues
- [ ] Review new API endpoint implementations
- [ ] Check database schema changes are compatible

### ✅ Testing
- [ ] Unit tests pass: `pytest -v`
- [ ] Manual testing of Human-in-the-Loop workflow completed
- [ ] New endpoints tested with JWT authentication
- [ ] Checkpoint persistence verified across restarts

### ✅ Documentation
- [ ] README.md updated with new version and endpoints
- [ ] CHANGELOG.md includes all changes
- [ ] Release notes are comprehensive
- [ ] API documentation generated/updated

### ✅ Dependencies
- [ ] `requirements.txt` includes `langgraph>=0.4.0`
- [ ] No conflicting package versions
- [ ] All dependencies available on PyPI

---

## Merge Steps

Choose **ONE** of the following merge strategies:

---

### Strategy A: Direct Merge (Recommended for Simple History)

**Use when:** You want to preserve all commit history

```bash
# Step 1: Ensure you're on the main branch
git checkout main

# Step 2: Pull latest changes from remote
git pull origin main

# Step 3: Merge the feature branch
git merge claude/clone-abp-agent-repo-011CUTMj7L4RuoUHQpUhKFNn

# Step 4: If conflicts occur, resolve them
# (Git will notify you of conflicts)
# Edit conflicting files, then:
git add <resolved-files>
git commit -m "Resolve merge conflicts"

# Step 5: Push to main
git push origin main
```

**Expected Result:**
- All commits from feature branch are added to main
- Merge commit created (if not fast-forward)
- Full commit history preserved

---

### Strategy B: Squash Merge (Recommended for Clean History)

**Use when:** You want a single commit for this entire feature

```bash
# Step 1: Ensure you're on the main branch
git checkout main

# Step 2: Pull latest changes
git pull origin main

# Step 3: Squash merge the feature branch
git merge --squash claude/clone-abp-agent-repo-011CUTMj7L4RuoUHQpUhKFNn

# Step 4: Create single commit with all changes
git commit -m "Release v3.1.0: Critical bug fixes and new endpoints

- Fix NameError crash in /agent/query and /agent/approve
- Implement persistent checkpointing with AsyncSqliteSaver
- Add 5 new API endpoints (Settings & Account Management)
- Enhance OAuthToken database schema
- Update documentation and CHANGELOG

See docs/v3.1.0_RELEASE_NOTES.md for details"

# Step 5: Push to main
git push origin main
```

**Expected Result:**
- Single commit on main with all changes
- Clean, linear history
- All feature commits condensed

---

### Strategy C: Rebase then Merge (For Linear History)

**Use when:** You want linear history with individual commits preserved

```bash
# Step 1: Checkout feature branch
git checkout claude/clone-abp-agent-repo-011CUTMj7L4RuoUHQpUhKFNn

# Step 2: Rebase onto latest main
git rebase main

# Step 3: If conflicts, resolve and continue
git add <resolved-files>
git rebase --continue

# Step 4: Switch to main and merge
git checkout main
git merge claude/clone-abp-agent-repo-011CUTMj7L4RuoUHQpUhKFNn

# Step 5: Push to main
git push origin main
```

**Expected Result:**
- Linear history (no merge commits)
- All individual commits preserved
- Commits appear chronological on main

---

### Strategy D: Pull Request Workflow (Recommended for Team Review)

**Use when:** You want formal code review process

```bash
# Step 1: Ensure feature branch is up-to-date and pushed
git checkout claude/clone-abp-agent-repo-011CUTMj7L4RuoUHQpUhKFNn
git pull origin claude/clone-abp-agent-repo-011CUTMj7L4RuoUHQpUhKFNn
git push origin claude/clone-abp-agent-repo-011CUTMj7L4RuoUHQpUhKFNn

# Step 2: Create pull request via GitHub/GitLab UI
# Navigate to: https://github.com/ssumakant/abp-agent
# Click "Pull Requests" → "New Pull Request"
# Base: main
# Compare: claude/clone-abp-agent-repo-011CUTMj7L4RuoUHQpUhKFNn

# Step 3: Fill in PR template
# Title: "Release v3.1.0: Critical Bug Fixes & New Endpoints"
# Description: Copy from docs/v3.1.0_RELEASE_NOTES.md Executive Summary

# Step 4: Request reviews (if applicable)

# Step 5: After approval, merge via GitHub UI
# Choose merge strategy (merge commit / squash / rebase)
# Click "Merge Pull Request"
```

**Expected Result:**
- PR creates audit trail
- Code review comments preserved
- Merge strategy chosen via UI

---

## Recommended Strategy

**For this release, I recommend Strategy B (Squash Merge)** because:

1. ✅ Creates clean, single commit for v3.1.0 release
2. ✅ All changes are cohesive (bug fixes + new features)
3. ✅ Easier to revert if issues found
4. ✅ Simpler git history for future reference
5. ✅ Detailed changes preserved in v3.1.0_RELEASE_NOTES.md

---

## Post-Merge Verification

After merging to main, verify the deployment:

### Step 1: Verify Git State

```bash
# Check current branch and commit
git log --oneline -5

# Verify all files are present
ls -la src/
ls -la docs/

# Check for uncommitted changes
git status
```

**Expected:** Clean working directory, v3.1.0 commit visible in log

---

### Step 2: Install Dependencies

```bash
# Activate virtual environment
source venv/bin/activate

# Install/upgrade dependencies
pip install -r requirements.txt --upgrade

# Verify langgraph version
pip show langgraph
# Should be >= 0.4.0
```

---

### Step 3: Run the Application

```bash
# Start the server
python -m src.main_refactored

# Or with uvicorn directly
uvicorn src.main_refactored:app --reload
```

**Expected output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

---

### Step 4: Test Critical Endpoints

#### Test 1: Health Check
```bash
curl http://localhost:8000/health
```

**Expected:**
```json
{
  "status": "healthy",
  "services": {
    "database": "connected",
    "llm": "configured",
    "graph": "initialized"
  }
}
```

---

#### Test 2: Agent Query (Fixed Endpoint)
```bash
# First create a test user (if not exists)
curl -X POST http://localhost:8000/users \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "testpass123",
    "internal_domain": "example.com",
    "timezone": "America/Los_Angeles"
  }'

# Then test agent query
curl -X POST http://localhost:8000/agent/query \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "<user-id-from-above>",
    "prompt": "How busy am I next week?"
  }'
```

**Expected:**
```json
{
  "user_id": "...",
  "response": "...",
  "thread_id": "...",
  "requires_approval": false
}
```

**Should NOT see:** `NameError: name 'graph' is not defined` ✅

---

#### Test 3: Settings Endpoint (New)
```bash
# Get JWT token first
TOKEN=$(curl -X POST http://localhost:8000/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=testpass123" \
  | jq -r '.access_token')

# Get settings
curl -X GET http://localhost:8000/api/v1/settings \
  -H "Authorization: Bearer $TOKEN"
```

**Expected:**
```json
{
  "user_id": "...",
  "work_hours": {
    "start": "09:00",
    "end": "17:00",
    "timezone": "America/Los_Angeles"
  },
  "protected_time_blocks": [...],
  "scheduling_rules": {...}
}
```

---

#### Test 4: Checkpoint Persistence
```bash
# Make a query that requires approval
curl -X POST http://localhost:8000/agent/query \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "<user-id>",
    "prompt": "Reschedule my 2pm meeting to tomorrow"
  }'

# Extract thread_id from response
THREAD_ID="<thread-id-from-response>"

# Verify checkpoints.db file was created
ls -lh checkpoints.db

# Restart the server
# Press Ctrl+C, then restart with:
python -m src.main_refactored

# Approve the action (should resume from checkpoint)
curl -X POST http://localhost:8000/agent/approve \
  -H "Content-Type: application/json" \
  -d '{
    "thread_id": "'$THREAD_ID'",
    "approved": true,
    "user_id": "<user-id>"
  }'
```

**Expected:** No "checkpoint not found" error ✅

---

### Step 5: Run Test Suite

```bash
# Run all tests
pytest -v

# Run with coverage
pytest --cov=src --cov-report=html
```

**Expected:** All tests pass (or at least same pass rate as before merge)

---

## Troubleshooting

### Issue 1: Merge Conflicts

**Symptom:** Git reports conflicts during merge

**Solution:**
```bash
# View conflicting files
git status

# For each conflict:
# 1. Open file in editor
# 2. Look for conflict markers:
#    <<<<<<< HEAD
#    (main branch code)
#    =======
#    (feature branch code)
#    >>>>>>> claude/clone-abp-agent-repo-011CUTMj7L4RuoUHQpUhKFNn

# 3. Choose which version to keep (or combine them)
# 4. Remove conflict markers

# 5. Mark as resolved
git add <file>

# 6. Complete merge
git commit -m "Resolve merge conflicts"
```

**Common Conflicts:**
- `CHANGELOG.md` - Keep both versions, newer at top
- `README.md` - Use feature branch version (has latest updates)
- `requirements.txt` - Combine and deduplicate

---

### Issue 2: Import Errors After Merge

**Symptom:**
```
ModuleNotFoundError: No module named 'langgraph.checkpoint.sqlite.aio'
```

**Solution:**
```bash
pip install langgraph --upgrade
pip install -r requirements.txt --force-reinstall
```

---

### Issue 3: Database Schema Mismatch

**Symptom:**
```
OperationalError: no such column: oauth_tokens.status
```

**Solution:**

The new columns should be added automatically by SQLAlchemy. If not:

```bash
# Backup database
cp abp_agent.db abp_agent.db.backup

# Delete database (will be recreated with new schema)
rm abp_agent.db

# Restart application (creates new database)
python -m src.main_refactored
```

**Or manually add columns:**
```sql
sqlite3 abp_agent.db

ALTER TABLE oauth_tokens ADD COLUMN account_email TEXT;
ALTER TABLE oauth_tokens ADD COLUMN status TEXT DEFAULT 'active';
ALTER TABLE oauth_tokens ADD COLUMN connected_at TEXT;
ALTER TABLE oauth_tokens ADD COLUMN is_primary INTEGER DEFAULT 0;

.quit
```

---

### Issue 4: Checkpoints.db Permission Errors

**Symptom:**
```
PermissionError: [Errno 13] Permission denied: 'checkpoints.db'
```

**Solution:**
```bash
# Ensure write permissions
chmod 664 checkpoints.db

# Or run with sudo (not recommended for production)
sudo python -m src.main_refactored
```

---

### Issue 5: Failed to Push to Main

**Symptom:**
```
error: failed to push some refs to 'origin'
```

**Possible Causes:**
1. **Branch Protection:** Main branch may have protection rules requiring PR
2. **Permission Denied:** Insufficient permissions to push to main
3. **Remote Ahead:** Remote main has commits you don't have locally

**Solution for Branch Protection:**
```bash
# Use Pull Request workflow instead (see Strategy D above)
```

**Solution for Permission Denied:**
```bash
# Contact repository administrator for write access
```

**Solution for Remote Ahead:**
```bash
git pull origin main --rebase
git push origin main
```

---

## Rollback Procedures

If critical issues are discovered after merge:

### Option A: Revert the Merge Commit

```bash
# Find the merge commit hash
git log --oneline -5

# Revert the merge
git revert -m 1 <merge-commit-hash>

# Push revert
git push origin main
```

**When to use:** Issues are discovered immediately, and you want a clear audit trail

---

### Option B: Hard Reset to Previous Commit

```bash
# DANGER: This rewrites history!
# Backup first
git branch backup-main main

# Find last good commit (before merge)
git log --oneline

# Hard reset
git reset --hard <last-good-commit-hash>

# Force push (requires force-push permissions)
git push origin main --force-with-lease
```

**When to use:** Issues are critical, and no one else has pulled the bad merge yet

**⚠️ WARNING:** Only use if you're absolutely sure no one has based work on the bad merge!

---

### Option C: Deploy Previous Version

Without changing git history:

```bash
# Checkout previous commit
git checkout <last-good-commit>

# Deploy from this commit
# (Keep main branch unchanged for now)
```

**When to use:** Emergency hotfix while you investigate the proper fix

---

## Safe Commit for Rollback

If you need to rollback, revert to this commit:

```
Commit: d5f4958
Message: Merge remote-tracking branch 'origin/claude/start-apb-agent-mvp-011CUSnZhaD48zBbFeduxTQP' into claude/clone-abp-agent-repo-011CUTMj7L4RuoUHQpUhKFNn
Date: Before v3.1.0 changes
```

---

## Final Verification Checklist

After merge and deployment:

- [ ] Application starts without errors
- [ ] `/health` endpoint returns 200 OK
- [ ] `/agent/query` endpoint does not crash with NameError
- [ ] `/agent/approve` endpoint works with saved checkpoints
- [ ] `checkpoints.db` file is created in application directory
- [ ] New settings endpoints (`/api/v1/settings`) return valid responses
- [ ] Account management endpoints (`/api/v1/auth/accounts`) work with JWT
- [ ] Database has new columns in `oauth_tokens` table
- [ ] Frontend can connect (if integrated)
- [ ] Unit tests pass
- [ ] No regressions in existing functionality

---

## Summary

**Recommended Merge Command:**

```bash
# Simple, clean, reversible merge
git checkout main
git pull origin main
git merge --squash claude/clone-abp-agent-repo-011CUTMj7L4RuoUHQpUhKFNn
git commit -m "Release v3.1.0: Critical bug fixes and new endpoints

- Fix NameError crash in /agent/query and /agent/approve endpoints
- Implement persistent checkpointing with AsyncSqliteSaver
- Add 5 new API endpoints for Settings & Account Management
- Enhance OAuthToken database schema with status tracking
- Update comprehensive documentation and CHANGELOG

Closes #<issue-number> (if applicable)

See docs/v3.1.0_RELEASE_NOTES.md for complete details"
git push origin main
```

---

## Support

If you encounter issues during merge:

1. **Check this document first** - Most issues covered above
2. **Review logs** - `git log`, application logs
3. **Check documentation** - `docs/v3.1.0_RELEASE_NOTES.md`
4. **Rollback if needed** - Use procedures above
5. **Contact team** - Slack / Email for assistance

---

**Prepared by:** Claude (AI Assistant)
**Date:** October 25, 2025
**Version:** v3.1.0
**Branch:** `claude/clone-abp-agent-repo-011CUTMj7L4RuoUHQpUhKFNn`

---

**Good luck with the merge! 🚀**
