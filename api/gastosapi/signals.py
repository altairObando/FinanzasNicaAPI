from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import Profile

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def crear_perfil_usuario(sender, instance, created, **kwargs):
    if created:
        Profile.objects.get_or_create(
            user=instance,            
        )

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def guardar_perfil_usuario(sender, instance, **kwargs):
    # Se asegura de actualizar el perfil si el usuario se guarda
    # Usamos getattr por seguridad en caso de que el perfil no exista aún
    if hasattr(instance, 'profile'):
        instance.profile.save()