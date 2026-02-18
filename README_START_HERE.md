# 🎯 START HERE - SmartQueue AI

## ⚡ Quick Start (3 Easy Steps)

### Step 1: Start Backend Server
**Double-click:** `1-start-backend.bat`

A black window will open showing:
```
Starting backend on http://localhost:8000
```

✅ **Keep this window open!**

---

### Step 2: Start Frontend Server
**Double-click:** `2-start-frontend.bat`

Another window will open showing:
```
Starting frontend on http://localhost:3000
```

✅ **Keep this window open too!**

---

### Step 3: Open in Browser
**Double-click:** `3-open-browser.bat`

Your browser will automatically open with:
- ✅ Test Connection Page
- ✅ Backend API Documentation

---

## 🧪 Test Everything Works

On the test page that opened, click **"Run All Tests"**

You should see:
- ✅ Backend Health Check - Success
- ✅ Healthcare Queue API - Success
- ✅ Banking Queue API - Success
- ✅ Create Test Token - Success
- ✅ WebSocket Connection - Success

---

## 🎉 Start Using the App

Once tests pass, visit:

**🏥 Healthcare Queue**
http://localhost:3000/healthcare.html

**🏦 Banking Queue**
http://localhost:3000/banking.html

**🏠 Home Page**
http://localhost:3000/index%20(2).html

---

## ❌ Troubleshooting

### Problem: "localhost refused to connect"

**Solution:** Make sure both batch files are running!
1. Check if you see TWO windows open (backend + frontend)
2. If not, run `1-start-backend.bat` and `2-start-frontend.bat` again

---

### Problem: "Port already in use"

**Solution:** Close any other programs using ports 8000 or 3000

Or use Task Manager:
1. Press `Ctrl + Shift + Esc`
2. Find "Python" processes
3. End them
4. Run the batch files again

---

### Problem: Test page shows errors

**Solution:** 
1. Close both server windows
2. Wait 5 seconds
3. Run `1-start-backend.bat` first
4. Wait until you see "Application startup complete"
5. Then run `2-start-frontend.bat`
6. Run `3-open-browser.bat`

---

## 📁 Project Structure

```
AI SMART QUEUE/
│
├── 1-start-backend.bat      ← Click this FIRST
├── 2-start-frontend.bat     ← Click this SECOND
├── 3-open-browser.bat       ← Click this THIRD
│
├── app/                     (Backend - FastAPI)
│   └── main.py
│
└── al smart queue frontend/ (Frontend - HTML/JS)
    ├── healthcare.html      (Create healthcare tokens)
    ├── banking.html         (Create banking tokens)
    ├── token.html           (View your token)
    └── test-connection.html (Test API connection)
```

---

## 🔧 What Each File Does

| File | Purpose |
|------|---------|
| `1-start-backend.bat` | Starts the Python FastAPI server |
| `2-start-frontend.bat` | Starts the web server for HTML files |
| `3-open-browser.bat` | Opens the app in your browser |
| `START_SERVERS.md` | Detailed manual instructions |
| `INTEGRATION_GUIDE.md` | Technical documentation |
| `QUICK_START.md` | Developer quick start guide |

---

## ✨ Features Available

✅ Create healthcare tokens with AI wait time prediction
✅ Create banking tokens with service routing
✅ Real-time queue position updates via WebSocket
✅ Download token as image
✅ Track your position in queue
✅ Admin dashboard (API ready, UI coming soon)

---

## 🆘 Still Having Issues?

1. **Check Python is installed:**
   ```
   python --version
   ```
   Should show: Python 3.x.x

2. **Check dependencies:**
   ```
   pip install -r requirements.txt
   ```

3. **Check if servers are running:**
   - Backend: http://localhost:8000
   - Frontend: http://localhost:3000

4. **Check browser console:**
   - Press F12 in browser
   - Look for error messages in Console tab

---

## 📞 Need More Help?

See detailed guides:
- `START_SERVERS.md` - Step-by-step server startup
- `INTEGRATION_GUIDE.md` - Full integration documentation
- `QUICK_START.md` - Developer quick reference

---

## 🎯 Next Steps After Setup

1. ✅ Test the connection
2. ✅ Create a healthcare token
3. ✅ Create a banking token
4. ✅ Track your token in real-time
5. ✅ Explore the API documentation

---

**Ready? Double-click `1-start-backend.bat` to begin! 🚀**
