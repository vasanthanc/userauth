#!python

from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$' , views.home , name = 'home'),
    url(r'^auth/$' , views.auth , name = 'evernote_auth'),
    #url(r'^notebook/[\w-]*/$' ,views.view_notebook_detail, name='view_notebook_detail'),
    url(r'^notebook/$' ,views.view_notebook_detail, name='view_notebook_detail'),
    url(r'^notebook/addnote/$' ,views.add_new_note, name='addnote'),
    url(r'^notebook/note/$' ,views.view_note_detail, name='view_notebook_detail'),
    url(r'callback/$' , views.callback , name = 'evernote_callback'),
]
