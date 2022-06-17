from __future__ import absolute_import
import os
from celery import Celery
from django.conf import settings
from django.core.mail import send_mail

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
app = Celery('project')

app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

@app.task(name='send_email_task')
def send_email_task(subject, message, from_email, to_email):
    print('Sending email...')
    print('Subject: {0}'.format(subject))
    print('Message: {0}'.format(message))
    print('From: {0}'.format(from_email))
    print('To: {0}'.format(to_email))
    send_mail(subject, message, from_email, to_email)
    return True