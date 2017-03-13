import hashlib, os.path, random, shutil

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import auth
from django.http import HttpResponse
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import SetPasswordForm

from .models import Account
from .forms import ( 
    UserCreationForm, SettingsForm,
    UserLoginForm, ForgotPassForm,
    AccountDeleteForm
)

def login(request):
    form = UserLoginForm()
    if request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return HttpResponse("success");
        else:
            try:
                user = Account.objects.get(email=username)
            except Account.DoesNotExist:
                user = None
            if user is None:
                return HttpResponse("failed")
            elif user.is_active == False:
                return HttpResponse(user.id)
            else:
                return HttpResponse("failed")
    context = {
        'next_page': request.GET.get('next', '/accounts/dashboard/'),
        'form': form,
        'user': None,
    }
    return render(request, 'accounts/login.html', context)

def register_user(request):
    form = UserCreationForm()
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            data = {}
            data['username'] = form.cleaned_data['username']
            data['email'] = form.cleaned_data['email']
            
            # Generate activation key
            rnum = str(random.random()).encode('utf8')   
            salt = hashlib.sha1(rnum).hexdigest()[:5]
            usernamesalt = data['username'] + salt
            usernamesalt = usernamesalt.encode('utf8')
            data['activation_key'] = hashlib.sha1(usernamesalt).hexdigest()
            
            user = form.save(data)
            if user is not None:
                form.sendEmail(data)

            return render(request, 'accounts/register_success.html')

    context = { 'form': form }
    return render(request, 'accounts/register.html', context)

@login_required(login_url='/accounts/login/')
def user_settings(request):
    data = {}
    data['email'] = request.user.email
    data['username'] = request.user.username
    form = SettingsForm(instance=request.user)

    if request.method == 'POST':
        form = SettingsForm(request.POST, request.FILES, instance=request.user)
        user_id = request.user.id
        if form.is_valid():
            form.save()
            
    context = {
        'username': data['username'],
        'email': data['email'],
        'form': form,
    }
    
    return render(request, 'accounts/user_settings.html', context)

@login_required(login_url='/accounts/login/')
def dashboard(request):
    context = {
        'user': request.user
    }
    return render(request, 'accounts/dashboard.html', context)

def logout(request):
    auth.logout(request)
    return redirect('/accounts/login')

@login_required(login_url='/accounts/login/')
def delete_user(request):
    current_user = request.user
    form = AccountDeleteForm()
    context = { 
        'username': current_user.username,
        'form': form,
    }
    if request.method == 'POST':
        form = AccountDeleteForm(request.POST)
        if form.is_valid():
            if form.cleaned_data['username'] == current_user.username:  
                current_id = str(current_user.id)
                auth.logout(request)
                current_user.delete()

                return render(request, 'accounts/delete_success.html')
            
            else:
                context['error'] = "Incorrect username."
                return render(request, 'accounts/delete_user.html', context)
        else:
            context['form'] = form
    return render(request, 'accounts/delete_user.html', context)

def activate_user(request, key):
    activation_expired = False
    already_active = False
    try:
        user = Account.objects.get(activation_key=key)
    except Account.DoesNotExist:
        user = None
    if user is not None:
        if user.is_active == False:
            if timezone.now() > user.key_expires:
                activation_expired = True #TODO: offer to resend activation
                baseurl = settings.SITE_BASE_URL + "/accounts/new_activation_link"
                context = {
                    'user_id': user.id,
                    'baseurl': baseurl,
                }
                return render(request, 'accounts/key_expired.html', context)
            else:
                user.is_active = True
                user.save()
                return render(request, 'accounts/activation_success.html')
        else:
            return render(request, 'accounts/activation_success.html')
    return render(request, 'accounts/error.html')
        

def new_activation_link(request, user_id):
    form = UserCreationForm()
    data = {}
    
    try:
        user = Account.objects.get(id=user_id)
    except Account.DoesNotExist:
        user = None
    
    if user is not None and not user.is_active:
        data['username'] = user.username
        data['email'] = user.email
        # Generate activation key
        rnum = str(random.random()).encode('utf8')   
        salt = hashlib.sha1(rnum).hexdigest()[:5]
        usernamesalt = data['username'] + salt
        usernamesalt = usernamesalt.encode('utf8')
        data['activation_key'] = hashlib.sha1(usernamesalt).hexdigest()
        user.activation_key = data['activation_key']
        user.key_expires = timezone.now() + timezone.timedelta(days=2)
        user.save()
        
        form.sendEmail(data)
        
        return redirect('/accounts/register_success')
    return redirect('/accounts/login')

def forgot_pass(request):
    if request.method == 'POST':
        form = ForgotPassForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            
            try:
                user = Account.objects.get(email=email)
            except Account.DoesNotExist:
                user = None
            
            if user is not None:
                rnum = str(random.random()).encode('utf8')   
                salt = hashlib.sha1(rnum).hexdigest()[:5]
                usernamesalt = user.username + salt
                usernamesalt = usernamesalt.encode('utf8')
                user.pwreset_key = hashlib.sha1(usernamesalt).hexdigest()
                user.pwreset_expires = timezone.now() + timezone.timedelta(hours=2)
                user.pwreset = True
                user.save()
                
                baseurl = settings.SITE_BASE_URL + "/accounts/r/"
                
                data = {}
                data['email'] = user.email
                data['username'] = user.username
                data['pwreset_key'] = user.pwreset_key
                data['user_id'] = user.id
                data['baseurl'] = baseurl
                
                form.sendEmail(data)

                context = {
                    'email': user.email,
                }
                return render(request, 'accounts/reset_confirm.html', context)
            else:
                return render(request, 'accounts/reset_nouser.html')
    else:
        context = {
            'form': ForgotPassForm(),
        }
    return render(request, 'accounts/forgot_pass.html', context)

def reset_view(request, user_id, pwreset_key):
    try:
        user = Account.objects.get(id=user_id)
    except Account.DoesNotExist:
        user = None
        
    if request.method == 'POST':
        form = SetPasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
            user.pwreset = False
            user.save()
            return render(request, 'accounts/reset_success.html')
        context = {
            'form': form,
        }
        return render(request, 'accounts/set_pass.html', context)
        
    if user is not None:
        if pwreset_key == user.pwreset_key and user.pwreset:
            if timezone.now() > user.pwreset_expires:
                baseurl = settings.SITE_BASE_URL + "/accounts/new_activation_link/"
                context = { 
                    'user_id': user.id,
                    'baseurl': baseurl,
                }
                return render(request, 'accounts/pwkey_expired.html', context)
            else:
                form = SetPasswordForm(user)
                context = {
                    'form': form,
                }
                return render(request, 'accounts/set_pass.html', context)
    
    return render(request, 'accounts/error.html')

@login_required(login_url='/accounts/login/')
def pass_settings(request):
    form = SetPasswordForm(request.user)
    context = {
        'username': request.user.username,
    }
    if request.method == 'POST':
        form = SetPasswordForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            user = auth.authenticate(username=request.user.email, password=request.POST.get('new_password1', ''))
            if user is not None:
                auth.login(request, user)
                context['success'] = "Password updated successfully."
                
    context['form'] = form

    return render(request, 'accounts/pass_settings.html', context)