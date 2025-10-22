from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import StreetActivity, Experience, Tag
from .forms import StreetActivityForm, ExperienceForm, TagForm

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
    form_class = ExperienceForm

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

    def get_context_data(self, **kwargs):
        """Extend context data to organize tags by category."""
        context = super().get_context_data(**kwargs)

        categories = {
            'needs': {
                'maintags': Tag.objects.filter(
                    nvc_category='needs',
                    maintag__isnull=True
                ).prefetch_related('subtags', 'experiences'),
                'standalone_tags': Tag.objects.filter(
                    nvc_category='needs',
                    maintag__isnull=True
                ).prefetch_related('experiences'),
                'tags': Tag.objects.filter(nvc_category='needs')
            },
            'feelings_fulfilled': {
                'maintags': Tag.objects.filter(
                    nvc_category='feelings_fulfilled',
                    maintag__isnull=True
                ).prefetch_related('subtags', 'experiences'),
                'standalone_tags': Tag.objects.filter(
                    nvc_category='feelings_fulfilled',
                    maintag__isnull=True
                ).prefetch_related('experiences'),
                'tags': Tag.objects.filter(nvc_category='feelings_fulfilled')
            },
            'feelings_unfulfilled': {
                'maintags': Tag.objects.filter(
                    nvc_category='feelings_unfulfilled',
                    maintag__isnull=True
                ).prefetch_related('subtags', 'experiences'),
                'standalone_tags': Tag.objects.filter(
                    nvc_category='feelings_unfulfilled',
                    maintag__isnull=True
                ).prefetch_related('experiences'),
                'tags': Tag.objects.filter(nvc_category='feelings_unfulfilled')
            },
            'other': {
                'maintags': Tag.objects.filter(
                    nvc_category='other',
                    maintag__isnull=True
                ).prefetch_related('subtags', 'experiences'),
                'standalone_tags': Tag.objects.filter(
                    nvc_category='other',
                    maintag__isnull=True
                ).prefetch_related('experiences'),
                'tags': Tag.objects.filter(nvc_category='other')
            }
        }
        context['categories'] = categories
        return context

class TagDetailView(DetailView):
    '''View to display details of a single tag.'''
    model = Tag
    context_object_name = 'tag'

class TagCreateView(CreateView):
    '''View to create a new tag.'''
    model = Tag
    form_class = TagForm

    def get_success_url(self):
        return reverse_lazy('tag-list')
