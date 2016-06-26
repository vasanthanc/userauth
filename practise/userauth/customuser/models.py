from __future__ import unicode_literals

from django.db import models

from django.contrib.auth.models import User
from django.db.models.signals import post_save

#class Employee(models.Model):
class EverNoteCredential(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    oauth_token = models.CharField(max_length=1000)
    oauth_token_secret = models.CharField(max_length=100)
    oauth_verifier = models.CharField(max_length=100)
    evernote_token = models.CharField(max_length=1000)

def create_evernote_credential(sender, instance, created, **kwargs):
    if created:
        profile, created = EverNoteCredential.objects.get_or_create(user=instance)
        post_save.connect(create_evernote_credential, sender=User)
