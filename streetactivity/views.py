from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import StreetActivity
from .forms import StreetActivityForm

class StreetActivityListView(ListView):
    '''View to list all street activities with filtering options.'''
    model = StreetActivity
    context_object_name = 'activities'
    paginate_by = 10

class StreetActivityDetailView(DetailView):
    '''View to display details of a single street activity.'''
    model = StreetActivity
    context_object_name = 'activity'

class StreetActivityCreateView(CreateView):
    '''View to create a new street activity.'''
    model = StreetActivity
    form_class = StreetActivityForm
    
    def get_success_url(self):
        return reverse_lazy('streetactivity_detail', kwargs={'pk': self.object.pk})

class StreetActivityUpdateView(UpdateView):
    '''View to update an existing street activity.'''
    model = StreetActivity
    form_class = StreetActivityForm

    def get_success_url(self):
        return reverse_lazy('streetactivity_detail', kwargs={'pk': self.object.pk})

class StreetActivityDeleteView(DeleteView):
    '''View to delete a street activity.'''
    model = StreetActivity
    template_name = 'admin/confirm_delete.html'
    success_url = reverse_lazy('streetactivity_list')
