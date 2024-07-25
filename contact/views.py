from django.conf import settings
from django.core.mail import send_mail
from django.shortcuts import render
from django.urls import reverse
from django.views.generic import TemplateView, FormView
from django.contrib.auth.models import User

from .forms import ContactForm


def contact(request):
    '''
    Renders the contact page with the dynamic mailto_url
    '''
    mailto_url = create_mailto_url()
    context = {'mailto_url':mailto_url}
    return render(request, 'contact/contact.html', context)

def about(request):
    '''
    Opens the about page'''
    mailto_url = create_mailto_url()
    context = {'mailto_url':mailto_url}
    return render(request, 'contact/about.html', context)

def help(request):
    '''Opens the help page'''
    return render(request, 'contact/help.html')

def create_mailto_url():
    '''Given the admin,
    creates a mailto url'''
    admin = User.objects.get(username='admin')
    mailto_url = f'mailto:{admin.email}'
    return mailto_url