from django.shortcuts import redirect, render
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import RegisterForm
from sociablecreating.views import get_logmessage_list_from_sociable_list

# Create your views here.
def register(request):
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
    user = request.user
    sociable_list = user.sociable_set.all()
    logmessage_list = get_logmessage_list_from_sociable_list(sociable_list)
    context = {
        'sociable_list'  : sociable_list,
        'logmessage_list': logmessage_list
        }
    return render(request, 'usermanagement/dashboard.html', context)