from django.views import generic
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.contrib import messages
from .models import Persona, Problem, Reaction
from .forms import PersonaForm, ProblemForm, ReactionForm

class PersonaListView(generic.ListView):
    """View to list all personas."""
    model = Persona
    context_object_name = 'personas'

class PersonaCreateView(generic.CreateView):
    """View to create a new persona along with its problems and reactions."""
    model = Persona
    form_class = PersonaForm

class PersonaUpdateView(generic.UpdateView):
    """View to update an existing persona along with its problems and reactions."""
    model = Persona
    form_class = PersonaForm

class PersonaDetailView(generic.DetailView):
    """View to display details of a persona."""
    model = Persona

class ProblemCreateView(generic.CreateView):
    """View to create a new problem for a specific persona."""
    model = Problem
    form_class = ProblemForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['persona'] = get_object_or_404(Persona, pk=self.kwargs['persona_pk'])
        return context

    def form_valid(self, form):
        persona = get_object_or_404(Persona, pk=self.kwargs['persona_pk'])
        form.instance.persona = persona
        messages.success(self.request, 'Probleem succesvol toegevoegd!')
        response = super().form_valid(form)
        if self.request.POST.get('add_another'):
            return redirect('create-problem', persona_pk=self.kwargs['persona_pk'])
        return response


    def get_success_url(self):
        return reverse_lazy('persona-detail', kwargs={'pk': self.kwargs['persona_pk']})

class ProblemDeleteView(generic.DeleteView):
    """View to delete a problem."""
    model = Problem
    template_name = 'admin/confirm_delete.html'

    def get_success_url(self):
        persona_pk = self.object.persona.pk
        messages.success(self.request, 'Probleem succesvol verwijderd!')
        return reverse_lazy('persona-detail', kwargs={'pk': persona_pk})

class ReactionCreateView(generic.CreateView):
    """View to create a new reaction for a specific persona."""
    model = Reaction
    form_class = ReactionForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['persona'] = get_object_or_404(Persona, pk=self.kwargs['persona_pk'])
        return context

    def form_valid(self, form):
        persona = get_object_or_404(Persona, pk=self.kwargs['persona_pk'])
        form.instance.persona = persona
        messages.success(self.request, 'Reactie succesvol toegevoegd!')
        response = super().form_valid(form)
        if self.request.POST.get('add_another'):
            return redirect('create-reaction', persona_pk=self.kwargs['persona_pk'])
        return response

    def get_success_url(self):
        return reverse_lazy('persona-detail', kwargs={'pk': self.kwargs['persona_pk']})

class ReactionDeleteView(generic.DeleteView):
    """View to delete a reaction."""
    model = Reaction
    template_name = 'admin/confirm_delete.html'

    def get_success_url(self):
        persona_pk = self.object.persona.pk
        messages.success(self.request, 'Reactie succesvol verwijderd!')
        return reverse_lazy('persona-detail', kwargs={'pk': persona_pk})
