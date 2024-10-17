from django.shortcuts import  redirect, render
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView
from game.views import calc_percentage_xp
from sociablecreating.views import get_sociables_for_dashboard
from .forms import RegisterForm, UserForm, ProfileForm


class Register(CreateView):
    '''The sign up functionality'''
    form_class = RegisterForm
    template_name = 'usermanagement/register.html'
    success_url = reverse_lazy('dashboard_sociable')

    def form_valid(self, form):
        '''After the user input is valid, it logs in and redirects towards its dashboard'''
        user = form.save()
        login(self.request, user)
        return redirect(self.success_url)


@login_required(login_url='login')
def dashboard_logmessage(request):
    '''Given the user,
    generates the overview of the logmessages, one per sociable'''
    list_sociable_logmessage = get_sociables_for_dashboard(request.user)
    percentage_xp = calc_percentage_xp(request.user)
    context = {
        'list_sociable_logmessage': list_sociable_logmessage,
        'percentage_xp': percentage_xp
        }
    return render(request, 'sociablecreating/dashboard_logmessage.html', context)


@login_required(login_url='login')
def dashboard_sociable(request):
    '''Given the owner, generates the overview of its sociables'''
    percentage_xp = calc_percentage_xp(request.user)
    context = {
        'percentage_xp': percentage_xp,
        }
    return render(request, 'sociablecreating/dashboard_sociable.html', context)


class UserDetail(DetailView):
    '''Generic display view to get to the profile of the user:
    https://docs.djangoproject.com/en/5.0/ref/class-based-views/generic-display/'''
    model = User
    slug_field = 'username'
    slug_url_kwarg = 'username'


@login_required
def update_profile(request):
    '''When the user navigates to his profile,
    it either gets the forms to update his profile or it post his changed settings'''
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, ('Bewerken van je profiel is geslaagd!'))
            return redirect('dashboard_logmessage')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user.profile)
    return render(request, 'auth/user_form.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })
