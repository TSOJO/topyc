import secrets
import string
from email.message import EmailMessage
import ssl
import smtplib

from config import GMAIL_EMAIL, GMAIL_APP_PASSWORD, PASSWORD_LENGTH

def check_tonbridge_email(email):
    return email.endswith('@tonbridge-school.org')

def generate_password():
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(PASSWORD_LENGTH))

def send_email(to_email, subject, body):
    email_message = EmailMessage()
    email_message['From'] = GMAIL_EMAIL
    email_message['To'] = to_email
    email_message['Subject'] = subject
    email_message.set_content(body)
    
    context = ssl.create_default_context()
    
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls(context=context)
        server.login(
            user=GMAIL_EMAIL,
            password=GMAIL_APP_PASSWORD
        )
        server.sendmail(
            from_addr=GMAIL_EMAIL,
            to_addrs=to_email,
            msg=email_message.as_string()
        )
