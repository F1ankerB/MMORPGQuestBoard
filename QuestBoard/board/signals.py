from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Comment
from .utils import send_email

@receiver(post_save, sender=Comment)
def send_comment_notification(sender, instance, created, **kwargs):
    if created:
        post_author_email = instance.post.author.user.email  # Предполагается, что у UserProfile есть связанный объект User с электронной почтой
        subject = f'Новый комментарий к вашему посту "{instance.post.title}"'
        message = f'{instance.user}: {instance.text}'
        send_email(subject, message, [post_author_email])

from django.db.models.signals import pre_save

@receiver(pre_save, sender=Comment)
def comment_approved_notification(sender, instance, **kwargs):
    if instance.id:
        previous = Comment.objects.get(id=instance.id)
        if not previous.approved and instance.approved:
            subject = 'Ваш комментарий был опубликован'
            message = f'Ваш комментарий к посту "{instance.post.title}" был одобрен и опубликован.'
            send_email(subject, message, [instance.user.user.email])
