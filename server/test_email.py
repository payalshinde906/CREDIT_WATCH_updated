import smtplib, ssl 
from email.mime.text import MIMEText 

smtp_host = "smtp.gmail.com" 
smtp_port = 465 
smtp_user = "payalshinde906@gmail.com" 
smtp_pass = "xshsfbzpouxuxclo" 

msg = MIMEText("This is a test email from CreditDataWatch") 
msg["Subject"] = "CreditDataWatch Email Test" 
msg["From"] = smtp_user 
msg["To"] = smtp_user 

try: 
    context = ssl.create_default_context() 
    with smtplib.SMTP_SSL(smtp_host, smtp_port, context=context) as server: 
        server.login(smtp_user, smtp_pass) 
        server.send_message(msg) 
        print("SUCCESS: Email sent!") 
except Exception as e: 
    print(f"FAILED: {e}")