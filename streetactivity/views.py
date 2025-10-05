from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import StreetActivity
from .forms import StreetActivityForm

class StreetActivityListView(ListView):
    '''View to list all non-helpneeded street activities with pagination.'''
    model = StreetActivity
    template_name = 'streetactivity/streetactivity_list.html'
    context_object_name = 'activities'
    paginate_by = 10
    ordering = ['name']
    queryset = StreetActivity.objects.filter(needHelp=False)

class StreetActivityDetailView(DetailView):
    '''View to display details of a single street activity.'''
    model = StreetActivity
    template_name = 'streetactivity/streetactivity_detail.html'
    context_object_name = 'activity'

class StreetActivityCreateView(CreateView):
    '''View to create a new street activity.'''
    model = StreetActivity
    form_class = StreetActivityForm
    template_name = 'streetactivity/streetactivity_form.html'
    success_url = reverse_lazy('streetactivity_list')

class StreetActivityUpdateView(UpdateView):
    '''View to update an existing street activity.'''
    model = StreetActivity
    form_class = StreetActivityForm
    template_name = 'streetactivity/streetactivity_form.html'

    def get_success_url(self):
        return reverse_lazy('streetactivity_detail', kwargs={'pk': self.object.pk})

class StreetActivityDeleteView(LoginRequiredMixin, DeleteView):
    '''View to delete a street activity.'''
    model = StreetActivity
    template_name = 'admin/confirm_delete.html'
    success_url = reverse_lazy('streetactivity_list')
    login_url = reverse_lazy('login')
