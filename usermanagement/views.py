from django.shortcuts import redirect, render
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from sociablecreating.views import get_logmessage_list_from_sociable_list
from .forms import RegisterForm

# Create your views here.
def register(request):
    '''Either renders the registerform for the user to fill in,
     Or given the posted registerform, creates a user and logs that user in'''
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(True)
            login(request, user)
            return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'usermanagement/register.html', {'form': form})

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
