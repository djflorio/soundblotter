from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth.decorators import login_required

def index(request):
    return render(request, 'pages/index.html')