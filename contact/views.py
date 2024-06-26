from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse
from django.views.generic import TemplateView, FormView
from django.contrib.auth.models import User

from .forms import ContactForm

def create_mailto_url():
    '''Given the admin,
    creates a mailto url'''
    admin = User.objects.get(username='admin')
    mailto_url = f'mailto:{admin.email}'
    return mailto_url

class SuccessView(TemplateView):
    '''When smtp is implemented, user will be redirected to a success page after entering the contact form'''
    template_name = 'contact/success.html'

class ContactView(FormView):
    
    form_class = ContactForm
    template_name = 'contact/contact.html'

    def get_success_url(self) -> str:
        return reverse('success')

    def form_valid(self, form):
        email = form.cleaned_data.get('email')
        subject = form.cleaned_data.get('subject')
        message = form.cleaned_data.get('message')

        full_message = f"""
            Receieved message below from {email}, {subject}
            __________________________


            {message}
"""
        send_mail(
            subject="Received contact from submission",
            message=full_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.NOTIFY_EMAIL],
        )
        return super(ContactView, self).form_valid(form)
