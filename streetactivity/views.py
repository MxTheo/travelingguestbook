from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import StreetActivity, Experience, Tag
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
        return reverse_lazy('streetactivity-detail', kwargs={'pk': self.object.pk})

class StreetActivityUpdateView(UpdateView):
    '''View to update an existing street activity.'''
    model = StreetActivity
    form_class = StreetActivityForm

    def get_success_url(self):
        return reverse_lazy('streetactivity-detail', kwargs={'pk': self.object.pk})

class StreetActivityDeleteView(DeleteView):
    '''View to delete a street activity.'''
    model = StreetActivity
    template_name = 'admin/confirm_delete.html'
    success_url = reverse_lazy('streetactivity-list')

class ExperienceListView(ListView):
    '''View to list all experiences.'''
    model = Experience
    context_object_name = 'experiences'
    paginate_by = 10

class ExperienceDetailView(DetailView):
    '''View to display details of a single experience.'''
    model = Experience
    context_object_name = 'experience'

class ExperienceCreateView(CreateView):
    '''View to create a new experience.'''
    model = Experience
    fields = ['report', 'fase', 'tags']

    def form_valid(self, form):
        activity_id = self.kwargs['pk']
        form.instance.activity_id = activity_id
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('experience-detail', kwargs={'pk': self.object.pk})
    
class TagListView(ListView):
    '''View to list all tags.'''
    model = Tag
    context_object_name = 'tags'
    paginate_by = 10

class TagDetailView(DetailView):
    '''View to display details of a single tag.'''
    model = Tag
    context_object_name = 'tag'

class TagCreateView(CreateView):
    '''View to create a new tag.'''
    model = Tag
    fields = ['name']

    def get_success_url(self):
        return reverse_lazy('tag-list')