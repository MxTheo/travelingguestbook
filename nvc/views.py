from django.views.generic.edit import FormView
from .forms import ObservationFormSet

class ObservationFormView(FormView):
    template_name = 'nvc/step1_observation.html'
    form_class = ObservationFormSet

    def get(self, request, *args, **kwargs):
        formset = ObservationFormSet()
        return self.render_to_response({'formset': formset})

    def post(self, request, *args, **kwargs):
        formset = ObservationFormSet(request.POST)
        if formset.is_valid():
            # Process the data here
            return super().form_valid(formset)
        return self.form_invalid(formset)