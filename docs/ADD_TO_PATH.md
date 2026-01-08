# Adding Python Scripts to Windows PATH

## Problem
```
WARNING: The scripts pip.exe, pip3.11.exe and pip3.exe are installed in 
'C:\Users\darko\AppData\Roaming\Python\Python311\Scripts' which is not on PATH.
```

## Solution: Add to PATH (Choose one method)

---

## Method 1: PowerShell (Quick & Easy) ✅ RECOMMENDED

Run this in PowerShell **as Administrator**:

```powershell
# Add to User PATH (recommended - doesn't need admin)
$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
$newPath = "C:\Users\darko\AppData\Roaming\Python\Python311\Scripts"
if ($userPath -notlike "*$newPath*") {
    [Environment]::SetEnvironmentVariable("Path", "$userPath;$newPath", "User")
    Write-Host "✅ Added to PATH successfully!" -ForegroundColor Green
    Write-Host "⚠️ Restart PowerShell for changes to take effect" -ForegroundColor Yellow
} else {
    Write-Host "Already in PATH" -ForegroundColor Yellow
}
```

**Then restart your PowerShell terminal.**

---

## Method 2: GUI (Windows Settings)

### Step-by-step:

1. **Open System Properties:**
   - Press `Win + R`
   - Type: `sysdm.cpl`
   - Press Enter

2. **Navigate to Environment Variables:**
   - Click "Advanced" tab
   - Click "Environment Variables..." button

3. **Edit PATH:**
   - Under "User variables" section, find `Path`
   - Click "Edit..."

4. **Add New Entry:**
   - Click "New"
   - Paste: `C:\Users\darko\AppData\Roaming\Python\Python311\Scripts`
   - Click "OK" on all dialogs

5. **Restart PowerShell**

---

## Method 3: Command Line (setx)

Run in PowerShell (will take effect in NEW terminals):

```powershell
$currentPath = [Environment]::GetEnvironmentVariable("Path", "User")
setx PATH "$currentPath;C:\Users\darko\AppData\Roaming\Python\Python311\Scripts"
```

**⚠️ Close and reopen PowerShell after running this.**

---

## Verify It Works

After adding to PATH and restarting PowerShell:

```powershell
# Check if pip is accessible
pip --version

# Should output something like:
# pip 24.x.x from C:\Users\darko\AppData\Roaming\Python\Python311\site-packages\pip (python 3.11)
```

---

## Quick Fix (Temporary - Current Session Only)

If you need pip RIGHT NOW without restarting:

```powershell
# Add to current session PATH only
$env:Path += ";C:\Users\darko\AppData\Roaming\Python\Python311\Scripts"

# Test
pip --version
```

This only works until you close PowerShell.

---

## Troubleshooting

### Issue: "pip still not found after adding to PATH"

**Solution:** You MUST restart PowerShell (or all terminals) for PATH changes to take effect.

### Issue: "Multiple Python versions conflict"

Check which pip you're using:
```powershell
Get-Command pip | Select-Object Source
```

### Issue: "Permission denied"

Run PowerShell as Administrator for system-wide changes, or use User PATH (doesn't need admin).

---

## Alternative: Use Full Path (No PATH needed)

You can always use the full path without modifying PATH:

```powershell
# Instead of: pip install package
# Use:
C:\Users\darko\AppData\Roaming\Python\Python311\Scripts\pip.exe install package
```

---

## Recommended Action

**Run this now in PowerShell:**

```powershell
# Add to PATH (User level - no admin needed)
$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
$newPath = "C:\Users\darko\AppData\Roaming\Python\Python311\Scripts"
if ($userPath -notlike "*$newPath*") {
    [Environment]::SetEnvironmentVariable("Path", "$userPath;$newPath", "User")
    Write-Host "✅ PATH updated!" -ForegroundColor Green
}

# Restart PowerShell, then test:
# pip --version
```

**After running, close and reopen PowerShell.**

---

## VS Code Integrated Terminal

If using VS Code terminal:
1. Add to PATH using method above
2. **Close VS Code completely**
3. Reopen VS Code
4. Test in new terminal

---

## Summary

✅ Easiest: Run PowerShell command (Method 1)  
✅ Permanent: Use GUI (Method 2)  
✅ Quick test: Temporary PATH (current session)  
✅ Always works: Use full path to pip.exe  

**Don't forget to restart your terminal!**
