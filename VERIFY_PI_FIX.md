# Verify the Fix on Your Raspberry Pi

The import fixes are already in Git! Let's verify you have them.

## Step 1: Check Your Current Commit

On your Raspberry Pi, run:

```bash
cd /home/admin/ARC
git log --oneline -1
```

**You should see:**
```
4f3aee0 Refactor app launch commands...
```

If you see a different/older commit, you need to pull:

```bash
git pull
```

## Step 2: Verify the Import Fix

Check that the import is correct:

```bash
head -10 /home/admin/ARC/arc/apps/calendar/main.py
```

**You should see:**
```python
from arc.core import config
from arc.core.ui_elements import *
```

**NOT:**
```python
import config  # ❌ OLD VERSION
```

## Step 3: If Still Showing Old Code

If you pulled but still see `import config`, you might have uncommitted changes preventing the pull. Try:

```bash
cd /home/admin/ARC
git status
```

If you see "modified" files, stash them:

```bash
git stash
git pull
git log --oneline -1  # Verify you're at 4f3aee0
```

## Step 4: Test It

Now test:

```bash
cd /home/admin/ARC && venv/bin/python arc/apps/calendar/main.py
```

## Still Not Working?

If the imports are correct (`from arc.core import config`) but you still get the error, the issue might be that you're not running from the ARC root directory. 

Make sure you ALWAYS run with:
```bash
cd /home/admin/ARC && venv/bin/python arc/apps/calendar/main.py
```

The `cd /home/admin/ARC &&` part is CRITICAL - it ensures Python can find the `arc` package!

## Quick Debug

Run this to see what's in your file:

```bash
grep "import config" /home/admin/ARC/arc/apps/calendar/main.py
```

- If you see **`from arc.core import config`** → Good! ✅
- If you see **`import config`** → Need to pull/update! ❌

---

## Summary

1. **Check commit**: Should be `4f3aee0`
2. **Check imports**: Should be `from arc.core import config`  
3. **Run from root**: Always `cd /home/admin/ARC && ...`
4. **Test**: Run an app and verify no errors!


