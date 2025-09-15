import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from config import settings

html_content = """
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <title>測試信件</title>
    <style>
        body {
            font-family: 'Arial', sans-serif;
            background-color: #f4f4f7;
            margin: 0;
            padding: 0;
        }
        .container {
            max-width: 600px;
            margin: 30px auto;
            background-color: #ffffff;
            border-radius: 10px;
            padding: 30px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        h1 {
            color: #4a90e2;
            text-align: center;
        }
        p {
            color: #333333;
            line-height: 1.6;
        }
        .button {
            display: inline-block;
            padding: 12px 25px;
            margin: 20px 0;
            font-size: 16px;
            color: #ffffff;
            background-color: #4a90e2;
            text-decoration: none;
            border-radius: 5px;
            text-align: center;
        }
        .footer {
            text-align: center;
            font-size: 12px;
            color: #999999;
            margin-top: 30px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>歡迎使用測試信件</h1>
        <p>這是一封 HTML 郵件測試信，內含簡單排版與按鈕樣式。</p>
        <p>你可以在這裡放置更多訊息，甚至圖片或連結。</p>
        <a href="https://www.example.com" class="button">前往網站</a>
        <div class="footer">
            &copy; 2025 小安公司. All rights reserved.
        </div>
    </div>
</body>
</html>
"""


msg = MIMEMultipart("alternative")
msg["Subject"] = "daily paper summary"
msg["From"] = settings.MAIL_FROM
msg["To"] = settings.MAIL_FROM
msg.attach(MIMEText(html_content, "html"))

# 使用 Gmail SMTP
with smtplib.SMTP(settings.MAIL_SERVER, settings.MAIL_PORT) as server:
    server.starttls()  # 啟用 TLS
    server.login(settings.MAIL_USERNAME, settings.MAIL_PASSWORD)  # Gmail App 密碼
    server.send_message(msg)
