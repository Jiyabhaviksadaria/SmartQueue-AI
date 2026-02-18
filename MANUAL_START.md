# 🚀 Manual Start Instructions

## If the .bat files don't work, follow these steps:

### Step 1: Open Command Prompt or PowerShell

**Method 1:** Press `Windows Key + R`, type `cmd`, press Enter

**Method 2:** Search for "Command Prompt" in Windows search

### Step 2: Navigate to Your Project Folder

Copy and paste this command (adjust the path if needed):
```bash
cd "C:\Users\JIYA SADARIA\OneDrive\Desktop\AI  SMART QUEUE"
```

### Step 3: Start the Backend

In the same command prompt, run:
```bash
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Application startup complete.
```

✅ **Leave this window open!**

### Step 4: Open ANOTHER Command Prompt

Open a second command prompt window (repeat Step 1)

Navigate to the frontend folder:
```bash
cd "C:\Users\JIYA SADARIA\OneDrive\Desktop\AI  SMART QUEUE\al smart queue frontend"
```

### Step 5: Start the Frontend

In this second command prompt, run:
```bash
python -m http.server 3000
```

You should see:
```
Serving HTTP on :: port 3000 (http://[::]:3000/) ...
```

✅ **Leave this window open too!**

### Step 6: Open Your Browser

Open your web browser and go to:

**Test Connection:**
```
http://localhost:3000/test-connection.html
```

**Healthcare Queue:**
```
http://localhost:3000/healthcare.html
```

**Backend API Docs:**
```
http://localhost:8000/docs
```

---

## Quick Copy-Paste Commands

### Terminal 1 (Backend):
```bash
cd "C:\Users\JIYA SADARIA\OneDrive\Desktop\AI  SMART QUEUE"
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### Terminal 2 (Frontend):
```bash
cd "C:\Users\JIYA SADARIA\OneDrive\Desktop\AI  SMART QUEUE\al smart queue frontend"
python -m http.server 3000
```

---

## Troubleshooting

### "No module named 'app'"
Make sure you're running the backend command from the main project folder, NOT from inside the `app` folder.

### "Address already in use"
Close any other programs using ports 8000 or 3000, or use different ports:

**Backend on port 8080:**
```bash
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8080
```

**Frontend on port 3001:**
```bash
python -m http.server 3001
```

Then update `al smart queue frontend/js/config.js` to use port 8080.

### Backend shows errors
Check if all dependencies are installed:
```bash
pip install fastapi uvicorn sqlalchemy pydantic python-jose passlib bcrypt python-multipart websockets scikit-learn pandas numpy
```

---

## To Stop the Servers

In each command prompt window:
1. Press `Ctrl + C`
2. Type `Y` if asked to confirm
3. Close the window

---

## Success Checklist

- [ ] Backend running - see "Application startup complete"
- [ ] Frontend running - see "Serving HTTP on :: port 3000"
- [ ] Can open http://localhost:8000/docs
- [ ] Can open http://localhost:3000/test-connection.html
- [ ] All tests pass on test page

Once all checked, you're ready! 🎉
