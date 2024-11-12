from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic.edit import FormView
from .forms import ObservationFormSet

def prepare_for_choice_of_observations_step_2(request):
    observations = request.session.get('observations', None)
    context = {'observations': observations}
    return render(request, 'nvc/step2_observation.html', context)

class ObservationFormView(FormView):
    """Step 1 of the multistep form to create a non-violent communication compliment
    Where user enters what they observed"""
    template_name = 'nvc/step1_observation.html'
    form_class = ObservationFormSet
    success_url = reverse_lazy('step2-observation')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['formset'] = self.get_form()
        return context

    def form_valid(self, formset):
        self.request.session['observations'] = formset.cleaned_data
        return super().form_valid(formset)

    def form_invalid(self, formset):
        return self.render_to_response(self.get_context_data(formset=formset))

    def post(self, request, *args, **kwargs):
        formset = self.get_form()
        if formset.is_valid():
            return self.form_valid(formset)
        else:
            return self.form_invalid(formset)

    def get_form(self, data=None):
        return self.form_class(data=data)