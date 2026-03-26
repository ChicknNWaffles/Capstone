from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Branch
from api.file_service import file_service


@receiver(post_save, sender=Branch)
def create_branch_s3_folder(sender, instance, created, **kwargs):
    if created:
        file_service.create_branch_folder(instance.project.id, instance.name)
