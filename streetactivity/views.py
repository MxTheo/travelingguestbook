import json
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from .models import StreetActivity, ExternalReference, SWOTElement, SWOTHistory
from .forms import StreetActivityForm, ExternalReferenceForm, SWOTElementForm, SWOTAlternativeForm

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

    def get_context_data(self, **kwargs):
        """Pre-filter SWOT elements by type for better performance"""
        context = super().get_context_data(**kwargs)
        activity = self.get_object()

        context['strengths'] = activity.swotelement_set.filter(element_type='S')
        context['weaknesses'] = activity.swotelement_set.filter(element_type='W')
        context['opportunities'] = activity.swotelement_set.filter(element_type='O')
        context['threats'] = activity.swotelement_set.filter(element_type='T')

        return context

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

class ExternalReferenceCreateView(CreateView):
    """View to create a new external reference for a specific street activity.
    """
    model = ExternalReference
    form_class = ExternalReferenceForm

    def form_valid(self, form):
        activity_id = self.kwargs['activity_id']
        form.instance.activity_id = activity_id
        messages.success(self.request, 'Bedankt voor je bijdrage!')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('streetactivity_detail', kwargs={'pk': self.object.activity.pk})

class SWOTElementListView(ListView):
    """
    View to list all SWOT elements with sorting options"""
    model = SWOTElement
    context_object_name = 'elements'
    paginate_by = 20

    def get_queryset(self):
        queryset = SWOTElement.objects.all()

        activity_pk = self.kwargs.get('pk')
        if activity_pk:
            queryset = queryset.filter(street_activity_id=activity_pk)

        element_type = self.request.GET.get('type')
        if element_type in ['S', 'W', 'O', 'T']:
            queryset = queryset.filter(element_type=element_type)

        sort_by = self.request.GET.get('sort', 'recent')
        if sort_by == 'popular':
            queryset = queryset.order_by('-recognition_count')
        elif sort_by == 'needs_voting':
            queryset = queryset.filter(needs_voting=True).order_by('-date_created')
        else:  # recent
            queryset = queryset.order_by('-date_created')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        activity_pk = self.kwargs.get('pk')
        if activity_pk:
            context['activity'] = get_object_or_404(StreetActivity, pk=activity_pk)
        return context

class SWOTElementCreateView(CreateView):
    """Create a new SWOT element"""
    model = SWOTElement
    form_class = SWOTElementForm

    def form_valid(self, form):
        activity_pk = self.kwargs.get('pk')
        if activity_pk:
            form.instance.street_activity = get_object_or_404(StreetActivity, pk=activity_pk)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('swotelement-list', kwargs={"pk":self.object.street_activity.pk})

class SWOTElementUpdateView(UpdateView):
    """Suggest alternative formulation"""
    model = SWOTElement
    form_class = SWOTAlternativeForm
    template_name = 'streetactivity/swotelement_update.html'
    
    def form_valid(self, form):
        """Only update alternative formulation, not the current formulation"""
        self.object.alternative_formulation = form.cleaned_data['alternative_formulation']
        self.object.needs_voting = True
        self.object.votes_current = 0
        self.object.votes_alternative = 0
        self.object.save()
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('swotelement-list', kwargs={"pk":self.object.street_activity.pk})

class SWOTElementDetailView(DetailView):
    """Detail view for a SWOT element with all versions"""
    model = SWOTElement
    context_object_name = 'element'

def recognize_swotelement(request, pk):
    """Like a like button, users can recognize swotelements. The count of recognitions are saved"""
    element = get_object_or_404(SWOTElement, pk=pk)

    if not request.session.session_key:
        request.session.create()

    recognition_key = f"recognized_{pk}"
    if not request.session.get(recognition_key):
        element.recognition_count += 1
        element.save()
        request.session[recognition_key] = True
        request.session.modified = True
        return JsonResponse({'success': True, 'new_count': element.recognition_count})

    return JsonResponse({'error': 'Al gedaan'}, status=400)

@require_POST
def vote_formulation(request, pk):
    """Vote for current vs alternative formulation"""
    element = get_object_or_404(SWOTElement, pk=pk)

    if not element.needs_voting:
        return JsonResponse({'error': 'Geen stemming actief'}, status=400)

    if not request.session.session_key:
        request.session.create()

    vote_key = f"voted_{pk}"
    if request.session.get(vote_key):
        return JsonResponse({'error': 'Al gestemd'}, status=400)

    data = json.loads(request.body)
    vote_for_current = data.get('vote_for_current', True)

    if vote_for_current:
        element.votes_current += 1
    else:
        element.votes_alternative += 1
    element.save()

    request.session[vote_key] = True
    request.session.modified = True

    # Check of stemming compleet is
    if element.votes_alternative >= 3 or element.votes_current >= 3:
        handle_formulation_voting(element)

    return JsonResponse({'success': True})


def handle_formulation_voting(element):
    """Afhandeling van stemresultaat"""
    if element.votes_alternative > element.votes_current:
        # Bewaar oude formulering in geschiedenis
        SWOTHistory.objects.create(
            swot_element=element,
            old_formulation=element.formulation,
            new_formulation=element.alternative_formulation
        )
        # Update naar nieuwe formulering
        element.formulation = element.alternative_formulation
    
    # Reset stemming
    element.alternative_formulation = None
    element.votes_current = 0
    element.votes_alternative = 0
    element.needs_voting = False
    element.save()
