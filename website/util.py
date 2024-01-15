import secrets
import string
from email.message import EmailMessage
import ssl
import smtplib

from config import GMAIL_EMAIL, GMAIL_APP_PASSWORD, PASSWORD_LENGTH
from website.model import Task, Lesson, Module

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

def get_previous_and_next_task(current_task):
    sorted_tasks = Task.query.join(Module, Task.module).order_by(Module.number.asc(), Task.number.asc()).all()
    sorted_lessons = Lesson.query.join(Module, Lesson.module).order_by(Module.number.asc()).all()
    
    sorted_tasks_and_lessons = []
    for t in sorted_tasks:
        while len(sorted_lessons) > 0 and sorted_lessons[0].module.number <= t.module.number:
            sorted_tasks_and_lessons.append(sorted_lessons.pop(0))
        sorted_tasks_and_lessons.append(t)
    sorted_tasks_and_lessons.extend(sorted_lessons)
    
    index = sorted_tasks_and_lessons.index(current_task)
    previous = None
    if index > 0:
        previous = sorted_tasks_and_lessons[index-1]
    next_ = None
    if index < len(sorted_tasks_and_lessons) - 1:
        next_ = sorted_tasks_and_lessons[index+1]
    
    return previous, next_

def is_lesson(x):
    return isinstance(x, Lesson)
