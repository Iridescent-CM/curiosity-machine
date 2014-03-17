from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib.auth import authenticate
from django.contrib import auth

def login(request):
    if request.method == 'GET':
        return render(request, 'login.html',)

    email = request.POST.get('email', None)
    password = request.POST.get('password', None)
    user = authenticate(email=email, password=password)          
    if user is not None:
        if user.is_active:
            auth.login(request, user)
            url = user.get_absolute_url()
            return HttpResponseRedirect(url)
        else:
            return render(request, 'login.html', {'message':'Your account is disabled.'})
    else:
        return render(request, 'login.html', {'message':'Invalid email or password.'})

