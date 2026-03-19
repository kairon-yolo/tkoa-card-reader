🟦 Step 1: Create a Dedicated Profile
Create a folder in PowerShell:
mkdir "C:\Users\XXXX\AppData\Local\Google\Chrome\AvalonProfile"

🟦 Step 2: Manually Launch Chrome Using This Profile
Run:
"C:\Program Files\Google\Chrome\Application\chrome.exe" --user-data-dir="C:\Users\XXXX\AppData\Local\Google\Chrome\AvalonProfile"
Chrome will open using this profile (it will be empty the first time).

🟦 Step 3: Manually Pass the Cloudflare Verification
Inside Chrome, go to:
https://w.atwiki.jp/avalononline-wiki/pages/32.html
You should see:
Verify you are human
Please manually:
Click the verification button
Wait for it to complete
Confirm that you can see the actual card page
⚠️ This step is critical. Without it, Selenium will always get stuck.

🟦 Step 4: Completely Close Chrome
Make sure all Chrome windows are closed. 
Then check in Task Manager to ensure:
No chrome.exe processes are still running.

🟦 Step 5: Let Selenium Use This Profile
In your Python script, configure:

CHROME_PROFILE = r"C:\Users\XXXX\AppData\Local\Google\Chrome\AvalonProfile"

options = webdriver.ChromeOptions()
options.add_argument(f"--user-data-dir={CHROME_PROFILE}")
options.add_argument("--profile-directory=Default")
options.add_argument("--start-maximized")

🟦 Step 6: Run Your Script
py -3.12 auto-download-cards.py

