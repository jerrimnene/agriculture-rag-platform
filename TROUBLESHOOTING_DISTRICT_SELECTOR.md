# 🔧 TROUBLESHOOTING: District Selector Not Working

**Date:** November 11, 2024  
**Issue:** District selector dropdown not working, no context displaying

---

## 🔍 DIAGNOSTIC STEPS

### Step 1: Open Browser Console
1. Open the frontend in browser
2. Press **F12** (or **Cmd+Option+I** on Mac)
3. Click on **Console** tab
4. Look for these messages:

**What you should see:**
```
Loading districts from API...
Districts loaded: 56 districts
Districts dropdown populated successfully
```

**If you see errors instead, continue to Step 2**

---

### Step 2: Check for JavaScript Errors

**Common errors:**

#### Error 1: "Failed to fetch"
```
Failed to load districts: TypeError: Failed to fetch
```
**Solution:** API is not running
```bash
# Check API status
curl http://localhost:8000/health

# If not running, restart:
cd /Users/providencemtendereki/agriculture-rag-platform
python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

#### Error 2: "CORS error"
```
Access to fetch at 'http://localhost:8000/districts' from origin 'null' has been blocked by CORS policy
```
**Solution:** Open file via HTTP server, not file://
```bash
# Option 1: Use Python's simple HTTP server
cd /Users/providencemtendereki/agriculture-rag-platform/frontend
python3 -m http.server 8080

# Then open: http://localhost:8080/index.html
```

#### Error 3: "handleDistrictChange is not defined"
**Solution:** JavaScript not loaded properly - hard refresh (Cmd+Shift+R)

---

### Step 3: Test District Selector Manually

Open browser console and run:
```javascript
// Test if function exists
typeof handleDistrictChange

// Should return: "function"

// Test if element exists
document.getElementById('districtSelect')

// Should return: <select id="districtSelect">

// Manually trigger district change
selectedDistrict = 'Buhera';
handleDistrictChange();

// Check console for: "handleDistrictChange called"
// Check console for: "Selected district: Buhera"
```

---

### Step 4: Hard Refresh Browser

**Clear all cache:**
1. **Safari:** Cmd+Option+E (Empty Caches), then Cmd+R
2. **Chrome:** Cmd+Shift+R (Hard Reload)
3. **Firefox:** Cmd+Shift+R (Hard Reload)

Or manually:
1. Open DevTools (F12)
2. Right-click on refresh button
3. Select "Empty Cache and Hard Reload"

---

## 🛠️ FIXES APPLIED

### Fix 1: Added Console Logging
Added debug console.log statements to track:
- When `loadDistricts()` is called
- When districts are loaded from API
- When dropdown is populated
- When `handleDistrictChange()` is called
- What district was selected

### Fix 2: Added Error Handling
- API fetch errors now show alert
- Console errors show detailed information
- HTTP status codes are checked

### Fix 3: Confirmed Event Handler
Verified `onchange="handleDistrictChange()"` attribute is present on line 360:
```html
<select id="districtSelect" onchange="handleDistrictChange()">
```

---

## 🔧 ALTERNATIVE: Run via HTTP Server

If file:// protocol causes CORS issues, run via HTTP server:

```bash
# Navigate to frontend directory
cd /Users/providencemtendereki/agriculture-rag-platform/frontend

# Start HTTP server on port 8080
python3 -m http.server 8080
```

Then open in browser:
```
http://localhost:8080/index.html
```

---

## ✅ VERIFICATION CHECKLIST

After fixing, verify these work:

- [ ] Districts dropdown is populated with options
- [ ] Can click and select a district (e.g., "Buhera")
- [ ] Console shows "handleDistrictChange called"
- [ ] Console shows "Selected district: Buhera"
- [ ] Console shows "District profile loaded: ..." with data
- [ ] Header badges show Region and Rainfall
- [ ] Chat shows "Location set to Buhera, Manicaland (Region IV)"
- [ ] Right sidebar shows Location Context section
- [ ] Right sidebar shows Challenges & Warnings section
- [ ] Right sidebar shows Local Markets section
- [ ] Right sidebar shows Where to Sell section

---

## 🐛 KNOWN ISSUES & SOLUTIONS

### Issue: Dropdown is empty
**Cause:** `loadDistricts()` not called or failed
**Solution:** 
1. Check console for errors
2. Verify API is running: `curl http://localhost:8000/districts`
3. Hard refresh browser

### Issue: Can select but nothing happens
**Cause:** `handleDistrictChange()` not being called
**Solution:**
1. Check console - should see "handleDistrictChange called"
2. If not, verify `onchange` attribute exists on select element
3. Try manually calling in console: `handleDistrictChange()`

### Issue: Selected but "selectedDistrict" is empty/null
**Cause:** Select element value not being read
**Solution:**
1. Check console - should see "Selected district: X"
2. If shows "Selected district: null", the select.value is not set
3. Verify option elements have `value` attribute

### Issue: API call fails
**Cause:** API endpoint returns error
**Solution:**
1. Test endpoint directly: `curl http://localhost:8000/api/district/Buhera/complete-profile`
2. Check API logs: `tail -f /tmp/agrievidence_api.log`
3. Restart API if needed

---

## 📞 QUICK DIAGNOSTIC COMMAND

Run this in browser console to diagnose everything:

```javascript
// Run diagnostics
console.log('=== DISTRICT SELECTOR DIAGNOSTICS ===');
console.log('API_BASE:', API_BASE);
console.log('selectedDistrict:', selectedDistrict);
console.log('districtSelect element:', document.getElementById('districtSelect'));
console.log('districtSelect options:', document.getElementById('districtSelect').options.length);
console.log('handleDistrictChange exists:', typeof handleDistrictChange);
console.log('loadDistricts exists:', typeof loadDistricts);

// Test API connection
fetch('http://localhost:8000/health')
    .then(r => r.json())
    .then(d => console.log('API Health:', d))
    .catch(e => console.error('API Error:', e));

// Try loading districts
loadDistricts()
    .then(() => console.log('Districts loaded successfully'))
    .catch(e => console.error('Failed to load districts:', e));
```

---

## 🚀 QUICK FIX COMMANDS

### Restart Everything:
```bash
# Kill API
lsof -ti:8000 | xargs kill -9

# Start API
cd /Users/providencemtendereki/agriculture-rag-platform
python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000 &

# Wait 3 seconds
sleep 3

# Test API
curl http://localhost:8000/health

# Open frontend via HTTP server
cd frontend
python3 -m http.server 8080 &

# Open in browser
open http://localhost:8080/index.html
```

---

## 📝 WHAT TO REPORT

If issue persists, check console and report:

1. **Browser & Version:** Chrome 120, Safari 17, Firefox 121, etc.
2. **Console Errors:** Copy exact error messages
3. **API Status:** Result of `curl http://localhost:8000/health`
4. **Districts Loaded:** Result of `curl http://localhost:8000/districts | python3 -m json.tool | head -20`
5. **Console Diagnostic:** Result of running diagnostic command above

---

## ✅ EXPECTED BEHAVIOR

When working correctly:

1. **Page loads:**
   - Console: "Loading districts from API..."
   - Console: "Districts loaded: 56 districts"
   - Console: "Districts dropdown populated successfully"
   - Console: "District count: 56, Doc count: 16311" (or similar)

2. **Select district "Buhera":**
   - Console: "handleDistrictChange called"
   - Console: "Selected district: Buhera"
   - Console: "District profile loaded: {district: 'Buhera', ...}"
   - UI: Header shows "Region IV" and "500-700mm"
   - UI: Chat shows "📍 Location set to Buhera, Manicaland (Region IV)"
   - UI: Right sidebar shows all 4 sections populated

3. **Ask question:**
   - Answer appears with grey citation box below
   - Citations show category, district, snippet, links

---

**If you follow these steps and it still doesn't work, please share the console output! 🔍**
