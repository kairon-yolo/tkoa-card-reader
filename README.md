🟦 第 1 步：建立一個專用 Profile
在 PowerShell 建立資料夾：

Code
mkdir "C:\Users\User\AppData\Local\Google\Chrome\AvalonProfile"
🟦 第 2 步：用這個 Profile 手動開啟 Chrome
執行：

Code
"C:\Program Files\Google\Chrome\Application\chrome.exe" --user-data-dir="C:\Users\User\AppData\Local\Google\Chrome\AvalonProfile"
Chrome 會用這個 Profile 開啟（第一次是空的）。

🟦 第 3 步：手動通過 Cloudflare 驗證
在 Chrome 裡輸入：

Code
https://w.atwiki.jp/avalononline-wiki/pages/32.html
你會看到：

Verify you are human

請手動：

點按驗證

等它通過

確認你能看到真正的卡片頁面

⚠️ 這一步非常重要，沒有做 Selenium 永遠會卡住。

🟦 第 4 步：完全關閉 Chrome
務必關掉所有 Chrome 視窗。

🟦 第 5 步：讓 Selenium 使用這個 Profile
在你的 Python 程式裡設定：

python
CHROME_PROFILE = r"C:\Users\User\AppData\Local\Google\Chrome\AvalonProfile"

options = webdriver.ChromeOptions()
options.add_argument(f"--user-data-dir={CHROME_PROFILE}")
options.add_argument("--profile-directory=Default")
options.add_argument("--start-maximized")
🟦 第 6 步：執行你的程式
Code
py -3.12 auto-download-cards.py


然後在 Task Manager 裡確認：

沒有任何 chrome.exe 還在跑
