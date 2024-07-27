from django.shortcuts import redirect, render
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from sociablecreating.views import get_logmessage_list_from_sociable_list
from .forms import RegisterForm
from django.views.generic import CreateView

class RegisterView(CreateView):
    '''The sign up functionality'''
    form_class = RegisterForm
    template_name = 'usermanagement/register.html'
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        '''After the user input is valid, it logs in and redirects towards its dashboard'''
        user = form.save()
        login(self.request, user)
        return redirect(self.success_url)

@login_required(login_url='login')
def dashboard(request):
    '''Given the user,
    generates its dashboard'''
    user = request.user
    sociable_list = user.sociable_set.all()
    logmessage_list = get_logmessage_list_from_sociable_list(sociable_list)
    context = {
        'sociable_list'  : sociable_list,
        'logmessage_list': logmessage_list
        }
    return render(request, 'usermanagement/dashboard.html', context)
