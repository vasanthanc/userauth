# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User

from .models import EverNoteCredential

# Define an inline admin descriptor for Employee model
# which acts a bit like a singleton
class EverNoteCredentialInline(admin.StackedInline):
    model = EverNoteCredential
    can_delete = False
    verbose_name_plural = 'evernote_credential'

                # Define a new User admin
class UserAdmin(BaseUserAdmin):
    inlines = (EverNoteCredentialInline, )
    # Re-register UserAdmin
    admin.site.unregister(User)
    admin.site.register(User,BaseUserAdmin)
