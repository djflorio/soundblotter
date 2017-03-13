from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth.decorators import login_required
from django.conf import settings
from browser_audio.models import AudioRecording
from pydub import AudioSegment
import os.path
import time

def delete_file(request):
    current_user = request.user
    file_url = request.POST['file_url']
    file_id = request.POST['id']
    upload_directory = settings.MEDIA_ROOT + 'audio_uploads/'
    if os.path.isfile(upload_directory + file_url):
        os.remove(upload_directory + file_url)
    to_be_deleted = AudioRecording.objects.get(id=file_id)
    to_be_deleted.delete()
    return HttpResponse("deleted")
    
def create_file(request):
    current_user=request.user
    user_id = current_user.id
    upload_directory = settings.MEDIA_ROOT + 'audio_uploads/' + str(user_id) + '/'
    if not os.path.exists(upload_directory):
        os.makedirs(upload_directory)
    time_recorded = str(time.time())
    file_name = time_recorded + '.wav'
    mp3_file_name = time_recorded + '.mp3'
    path = upload_directory + file_name
    mp3_path = upload_directory + mp3_file_name
    
    current_user.audiorecording_set.create(title=mp3_file_name, file_url=str(user_id) + '/' + mp3_file_name)
    
    f = request.FILES['file']
    destination = open(path, 'wb+')
    for chunk in f.chunks():
        destination.write(chunk)
    destination.close()
    
    # Convert to Mp3
    AudioSegment.from_wav(path).export(mp3_path, format="mp3")
    # Delete wav file
    os.remove(path)
    
    return HttpResponse(path)

def rename_audio(request):
    audio_name = request.POST['audio_name']
    audio_id = request.POST['audio_id']
    recording = AudioRecording.objects.get(id=audio_id)
    if recording is not None:
        recording.title = audio_name
        recording.save()
    
    return HttpResponseRedirect('/audio/')

@login_required(login_url='/accounts/login/')
@ensure_csrf_cookie
def audio(request):
    current_user=request.user
    user_id = current_user.id
    user_name = current_user.username
    upload_directory = settings.MEDIA_ROOT + 'audio_uploads/' + str(user_id) + '/'
    if not os.path.exists(upload_directory):
        os.makedirs(upload_directory)
    upload_url = settings.MEDIA_URL + 'audio_uploads/' + str(user_id) + '/'
    
    context = {
        'audio_files': current_user.audiorecording_set.all(),
        'upload_url': settings.MEDIA_URL + 'audio_uploads/',
        'username': user_name,
    }
    
    return render(request, 'browser_audio/audio.html', context)