# 🚨 FIX YOUR RASPBERRY PI NOW

You're seeing `ModuleNotFoundError: No module named 'config'` because your Raspberry Pi has the old code with incorrect imports.

## ✅ Solution (Run on Raspberry Pi):

```bash
# 1. Go to your ARC directory
cd /home/admin/ARC

# 2. Pull the latest updates (this includes all import fixes!)
git pull

# 3. Test an app
cd /home/admin/ARC && venv/bin/python arc/apps/calendar/main.py
```

That's it! The import fixes are already done and committed.

## What Was Fixed

All 21 app files were updated from:
```python
import config  # ❌ Old - doesn't work
```

To:
```python
from arc.core import config  # ✅ New - works!
```

## After `git pull`, your apps will have the correct imports and will work immediately! 🎉

---

## If `git pull` doesn't work:

If you have local changes that conflict, stash them first:

```bash
cd /home/admin/ARC
git stash
git pull
```

Then test:
```bash
cd /home/admin/ARC && venv/bin/python arc/apps/calendar/main.py
```

## Verify the Fix

After pulling, check that the imports are correct:

```bash
head -n 10 /home/admin/ARC/arc/apps/calendar/main.py
```

You should see:
```python
from arc.core import config
from arc.core.ui_elements import *
```

If you see these lines, the fix is applied! ✅

## Launch the GUI

Once pulled, launch the full interface:

```bash
cd /home/admin/ARC
venv/bin/python launcher.py
```

All apps should now work when clicked! 🚀


