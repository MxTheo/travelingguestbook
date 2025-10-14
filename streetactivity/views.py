from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import StreetActivity
from .forms import StreetActivityForm

# views.py
class StreetActivityListView(ListView):
    '''View to list all street activities with filtering options.'''
    model = StreetActivity
    context_object_name = 'activities'
    paginate_by = 10

    def get_queryset(self):
        '''Filter the queryset based on the 'filter' GET parameter.'''
        queryset = StreetActivity.objects.all()

        filter_param = self.request.GET.get('filter')
        if filter_param == 'help_needed':
            return queryset.filter(needHelp=True)
        else:
            return queryset.filter(needHelp=False)

    def get_context_data(self, **kwargs):
        '''Add additional context data for the template.'''
        context = super().get_context_data(**kwargs)
        context['help_needed_count'] = StreetActivity.objects.filter(needHelp=True).count()
        context['has_help_needed'] = StreetActivity.objects.filter(needHelp=True).exists()
        return context

class StreetActivityDetailView(DetailView):
    '''View to display details of a single street activity.'''
    model = StreetActivity
    context_object_name = 'activity'

class StreetActivityCreateView(CreateView):
    '''View to create a new street activity.'''
    model = StreetActivity
    form_class = StreetActivityForm
    success_url = reverse_lazy('streetactivity_list')

class StreetActivityUpdateView(UpdateView):
    '''View to update an existing street activity.'''
    model = StreetActivity
    form_class = StreetActivityForm

    def get_success_url(self):
        return reverse_lazy('streetactivity_detail', kwargs={'pk': self.object.pk})

class StreetActivityDeleteView(LoginRequiredMixin, DeleteView):
    '''View to delete a street activity.'''
    model = StreetActivity
    template_name = 'admin/confirm_delete.html'
    success_url = reverse_lazy('streetactivity_list')
    login_url = reverse_lazy('login')
