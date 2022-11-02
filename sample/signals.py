from django.dispatch import receiver
from django.utils import timezone

from model_clone.signals import post_clone_save, pre_clone_save

from .models import Edition


@receiver(pre_clone_save, sender=Edition)
def increase_seq(sender, instance, **kwargs):
    instance.seq += 1


@receiver(post_clone_save, sender=Edition)
def update_book_published_at(sender, instance, **kwargs):
    if instance.book:
        instance.book.published_at = timezone.now()
        instance.book.save(update_fields=["published_at"])
