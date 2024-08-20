from django.shortcuts import render
from django.contrib.auth.models import User


def contact(request):
    '''
    Renders the contact page with the dynamic mailto_url
    '''
    mailto_url = create_mailto_url()
    context = {'mailto_url': mailto_url}
    return render(request, 'contact/contact.html', context)


def about(request):
    '''
    Opens the about page'''
    mailto_url = create_mailto_url()
    context = {'mailto_url': mailto_url}
    return render(request, 'contact/about.html', context)


def helppage(request):
    '''Opens the help page'''
    return render(request, 'contact/help.html')


def create_mailto_url():
    '''Given the admin,
    creates a mailto url'''
    admin = User.objects.get(is_superuser=True)
    mailto_url = f'mailto:{admin.email}'
    return mailto_url
