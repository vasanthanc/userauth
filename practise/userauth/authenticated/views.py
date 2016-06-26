from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from evernote.api.client import EvernoteClient
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from customuser.models import EverNoteCredential
from django.db import IntegrityError
from evernote.edam.notestore.ttypes import NoteFilter, NotesMetadataResultSpec
from evernote.edam.type.ttypes import NoteSortOrder,Note
from django.utils.html import escape
from django.http import HttpResponse
##This view shows after the user is authenticated

EN_CONSUMER_KEY = 'vinnarasan-6061'
EN_CONSUMER_SECRET = '2bb8129d411d0383'

def get_evernote_client(token=None):
    if token:
        return EvernoteClient(token=token , sandbox = True)
    else:
        return EvernoteClient(
            consumer_key = EN_CONSUMER_KEY ,
            consumer_secret = EN_CONSUMER_SECRET ,
            sandbox = True
        )



@login_required(login_url='login/')
def home(request):
    notebooks = ""
    try:
        user_obj = User.objects.get(username=request.user.get_username())
        oauth_verifier = user_obj.evernotecredential.oauth_verifier
        evernote_token = user_obj.evernotecredential.evernote_token
        client = get_evernote_client(evernote_token)
        note_store = client.get_note_store()
        userStore = client.get_user_store()
        notebooks = note_store.listNotebooks()
    except KeyError as key_error:
        print "{}:{}".format(key_error.args,key_error.message)
    except Exception as exp:
        return render(request,'home.html')

    return render(request,'home.html', {'notebooks': notebooks,'username':request.user.get_username()})

@login_required(login_url='login/')
def view_notebook_detail(request):
    if request.method == "POST":
        notes_values = ""
        try:
            user_obj = User.objects.get(username=request.user.get_username())
            evernote_token = user_obj.evernotecredential.evernote_token
            client = get_evernote_client(evernote_token)
            note_store = client.get_note_store()
            userStore = client.get_user_store()
            updated_filter = NoteFilter(notebookGuid=request.POST.get("guid_", ""))
            offset = 0
            max_notes = 10
            result_spec = NotesMetadataResultSpec(includeTitle=True)
            notes = note_store.findNotesMetadata(updated_filter, offset, max_notes, result_spec)
            notes_values = notes.notes
        except Exception as e:
            print "{}:{}".format(e.args,e.message)
            raise

        return render(request,'notes.html', {'notes': notes_values, 'notebook_id' : request.POST.get("guid_", ""),'username' : request.user.get_username()})


@login_required(login_url='login/')
def view_note_detail(request):
    string_content = ""
    if request.method == "POST":
        notes = ""
        try:
            user_obj = User.objects.get(username=request.user.get_username())
            oauth_verifier = user_obj.evernotecredential.oauth_verifier
            evernote_token = user_obj.evernotecredential.evernote_token
            client = get_evernote_client(evernote_token)
            note_store = client.get_note_store()
            note = note_store.getNote(request.POST.get("guid_", ""),True,True,False,False)
            string_content = note.content
        except Exception as e:
            print "{}:{}".format(e.args,e.message)
            raise
        return HttpResponse(escape(string_content))

@login_required(login_url='login/')
def add_new_note(request):
    if request.method == "POST":
        try:
            nBody = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
            nBody += "<!DOCTYPE en-note SYSTEM \"http://xml.evernote.com/pub/enml2.dtd\">"
            nBody += "<en-note>%s</en-note>" % request.POST.get("desc", "")
            ourNote = Note()
            ourNote.title = request.POST.get("title", "")
            ourNote.content = nBody
            ourNote.notebookGuid = request.POST.get("notebook_guid", "")
            user_obj = User.objects.get(username=request.user.get_username())
            evernote_token = user_obj.evernotecredential.evernote_token
            client = get_evernote_client(evernote_token)
            note_store = client.get_note_store()
            note = note_store.createNote(ourNote)
        except Exception as ex:
            print ex

        return redirect('/')

@login_required(login_url='login/')
def auth(request):
    client = get_evernote_client()
    callbackUrl = 'http://%s%s' % (
        request.get_host(), reverse('evernote_callback'))
    request_token = client.get_request_token(callbackUrl)
    request.session['oauth_token'] = request_token['oauth_token']
    request.session['oauth_token_secret'] = request_token['oauth_token_secret']
    return redirect(client.get_authorize_url(request_token))

@login_required(login_url='login/')
def callback(request):
    try:
        client = get_evernote_client()
        client.get_access_token(
            request.session['oauth_token'],
            request.session['oauth_token_secret'],
            request.GET.get('oauth_verifier', '')
        )
        user_obj = User.objects.get(username=request.user.get_username())
        ever_obj = EverNoteCredential(user= user_obj, oauth_token= request.session['oauth_token'], oauth_token_secret= request.session['oauth_token_secret'], oauth_verifier= request.GET.get('oauth_verifier', ''), evernote_token= client.token)
        ever_obj.save()
    except IntegrityError:
        EverNoteCredential.objects.filter(user_id=user_obj.id).update(oauth_token= request.session['oauth_token'], oauth_token_secret= request.session['oauth_token_secret'], oauth_verifier= request.GET.get('oauth_verifier', ''), evernote_token= client.token)

    except KeyError:
        return redirect('/')
    return  redirect('/')

