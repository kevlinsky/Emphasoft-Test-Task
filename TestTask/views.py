import random

from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect, render
from django.views.generic import CreateView, FormView

from Emphasoft import settings
from . import forms

import vk

from .forms import RegistrationForm


class RegistrationView(CreateView):
    template_name = 'register.html'
    form_class = RegistrationForm

    def post(self, request, *args, **kwargs):
        form = RegistrationForm(request.POST)
        errors = form.errors
        if form.is_valid():
            user = form.save(request.POST.copy())
            auth.login(request, user)
            return redirect('profile')
        else:
            return render(request, 'register.html', context={'errors': errors})


class AuthorizationView(FormView):
    template_name = 'login.html'
    form_class = forms.AuthorizationForm

    def post(self, request, *args, **kwargs):
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(username=username, password=password)
        if user is not None and user.is_active:
            auth.login(request, user)
            return redirect('profile')
        else:
            return render(request, 'login.html', context={'error': 'Incorrect username or password'})


@login_required
def profile(request):
    user = auth.get_user(request)
    try:
        social = user.social_auth.get(provider='vk-oauth2')
        access_token = social.extra_data['access_token']
        session = vk.Session(access_token=access_token)
        api = vk.API(session=session, v=settings.VK_API_VERSION)
        friends_ids = api.friends.get()['items']
        user_ids = ''
        for i in range(0, 5):
            if i == 0:
                user_ids += str(friends_ids[random.randint(0, len(friends_ids) - 1)])
            else:
                user_ids += ', ' + str(friends_ids[random.randint(0, len(friends_ids) - 1)])
        friends = api.users.get(user_ids=user_ids, fields='photo_100')
        return render(request, 'profile.html', context={'user': user, 'friends': friends})
    except ObjectDoesNotExist:
        return render(request, 'profile.html', context={'user': user})


def index(request):
    return render(request, 'index.html', context={'authenticated': request.user.is_authenticated})


def logout(request):
    auth.logout(request)
    return redirect('index')
