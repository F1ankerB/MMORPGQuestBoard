from django.core.mail import send_mail
def send_email(subject, message, recipient_list):
    send_mail(subject, message, 'te4kkaunt@yandex.ru', recipient_list)

from django.core.mail import send_mail
from django.conf import settings
from .models import UserProfile

def send_bulk_email(subject, message):
    recipients = [user.user.email for user in UserProfile.objects.all() if user.user.email]
    send_mail(subject, message, 'te4kkaunt@yandex.ru', recipients, fail_silently=False)