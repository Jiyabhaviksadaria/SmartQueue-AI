# 🚀 SmartQueue AI - Startup Guide

Choose ONE of the methods below to start the application.

## Method 1: The Easy Way (Using Batch Files)
This is the recommended way to start the application.

1. Double-click **`1-start-backend.bat`**
   - *A black window will open. Leave it running!*
2. Double-click **`2-start-frontend.bat`** 
   - *Another window will open. Leave it running too!*
3. Double-click **`3-open-browser.bat`**
   - *This will automatically launch the test page in your web browser.*

---

## Method 2: Manual Start (If Batch Files Fail)
Use this method if the batch files do not work on your system.

### Step 1: Start Backend
1. Open Command Prompt (`Win + R`, type `cmd`, press Enter)
2. Copy and run this exact command:
   ```cmd
   cd "C:\Users\JIYA SADARIA\OneDrive\Desktop\projects\AI  SMART QUEUE"
   python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
   ```
3. Wait until you see `Application startup complete`. **Keep the window open!**

### Step 2: Start Frontend
1. Open a **NEW** Command Prompt window (`Win + R`, type `cmd`, press Enter)
2. Copy and run this command:
   ```cmd
   cd "C:\Users\JIYA SADARIA\OneDrive\Desktop\projects\AI  SMART QUEUE\al smart queue frontend"
   python -m http.server 3000
   ```
3. Wait until you see `Serving HTTP on :: port 3000`. **Keep the window open!**

### Step 3: Open Application
Open your web browser and visit:
- **Test Connection Page**: http://localhost:3000/test-connection.html
- **Healthcare Queue**: http://localhost:3000/healthcare.html
- **Banking Queue**: http://localhost:3000/banking.html
- **Backend API Docs**: http://localhost:8000/docs

---

## 🛑 Troubleshooting

**1. "localhost refused to connect"**
Make sure BOTH the backend window and frontend window are open and running without errors.

**2. "Port already in use"**
Close other programs, run `check-setup.bat`, or restart your computer. You can also modify the batch files to use port `8080` (backend) or `3001` (frontend) if needed.

**3. "No module named app"**
Make sure you are running the backend command from the root project folder, NOT from inside the `app` folder itself.

**4. Where can I find API documentation?**
For detailed developer instructions, architectural details, and API integration, see **`QUICK_START.md`** and **`INTEGRATION_GUIDE.md`**.
