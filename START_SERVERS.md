# 🚀 How to Start SmartQueue AI

## Step-by-Step Instructions

### Step 1: Start the Backend Server

Open a **NEW Command Prompt** or **PowerShell** window and run:

```bash
cd "C:\Users\JIYA SADARIA\OneDrive\Desktop\AI  SMART QUEUE\app"
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

You should see output like:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**Keep this window open!** The backend server is now running.

### Step 2: Start the Frontend Server

Open **ANOTHER NEW** Command Prompt or PowerShell window and run:

```bash
cd "C:\Users\JIYA SADARIA\OneDrive\Desktop\AI  SMART QUEUE\al smart queue frontend"
python -m http.server 3000
```

You should see:
```
Serving HTTP on :: port 3000 (http://[::]:3000/) ...
```

**Keep this window open too!** The frontend server is now running.

### Step 3: Open Your Browser

Open your web browser and go to:

**Main App:** http://localhost:3000/index%20(2).html

**Test Connection:** http://localhost:3000/test-connection.html

**Healthcare Queue:** http://localhost:3000/healthcare.html

**Backend API Docs:** http://localhost:8000/docs

## Quick Test

1. Open http://localhost:3000/test-connection.html
2. Click "Run All Tests"
3. All tests should show green ✓

## Troubleshooting

### "Address already in use" error

**For port 8000:**
```bash
# Find what's using port 8000
netstat -ano | findstr :8000

# Kill the process (replace PID with the number from above)
taskkill /PID <PID> /F
```

**For port 3000:**
```bash
# Find what's using port 3000
netstat -ano | findstr :3000

# Kill the process
taskkill /PID <PID> /F
```

### Backend won't start

Check if all dependencies are installed:
```bash
pip install fastapi uvicorn sqlalchemy pydantic python-jose passlib bcrypt python-multipart websockets scikit-learn pandas numpy
```

### Frontend shows blank page

Make sure you're accessing the correct URL:
- ✓ http://localhost:3000/index%20(2).html
- ✗ http://localhost:3000/index.html (this file doesn't exist)

### API calls fail

1. Make sure BOTH servers are running
2. Check the backend terminal for errors
3. Open http://localhost:8000/docs to verify backend is working
4. Check browser console (F12) for error messages

## Alternative: Use Different Ports

If ports 8000 or 3000 are busy, you can use different ones:

**Backend on port 8080:**
```bash
cd app
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8080
```

**Frontend on port 3001:**
```bash
cd "al smart queue frontend"
python -m http.server 3001
```

Then update `al smart queue frontend/js/config.js`:
```javascript
const API_CONFIG = {
    BASE_URL: 'http://localhost:8080',  // Changed from 8000
    WS_URL: 'ws://localhost:8080'
};
```

## Stopping the Servers

To stop the servers:
1. Go to each terminal window
2. Press `CTRL + C`
3. Close the terminal windows

## Next Steps

Once both servers are running:
1. ✅ Test the connection: http://localhost:3000/test-connection.html
2. ✅ Try creating a healthcare token: http://localhost:3000/healthcare.html
3. ✅ View your token with real-time updates
4. ✅ Check the admin dashboard (coming soon)

## Need Help?

If you're still having issues:
1. Take a screenshot of any error messages
2. Check both terminal windows for error output
3. Open browser DevTools (F12) and check the Console tab
4. Verify both URLs work:
   - Backend: http://localhost:8000
   - Frontend: http://localhost:3000
