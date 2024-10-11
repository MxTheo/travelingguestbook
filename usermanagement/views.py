from django.shortcuts import  redirect, render
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from game.views import calc_percentage_xp
from sociablecreating.views import get_logmessage_list_from_sociable_list
from .forms import RegisterForm, UserForm, ProfileForm
from django.views.generic import CreateView, DetailView


class Register(CreateView):
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
    percentage_xp = calc_percentage_xp(user)
    context = {
        'sociable_list'  : sociable_list,
        'logmessage_list': logmessage_list,
        'percentage_xp'  : percentage_xp
        }
    return render(request, 'usermanagement/dashboard.html', context)


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
            return redirect('dashboard')
    else:
        user_form = UserForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user.profile)
    return render(request, 'auth/user_form.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })
