from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from .models import Goal
from django.views import generic
from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import Count


class GoalCreate(LoginRequiredMixin, generic.edit.CreateView):
    model       = Goal
    fields      = ['name']
    success_url = reverse_lazy('goals')

    def form_valid(self, form):
        form.instance.creator   = self.request.user
        form.instance.nr_chosen = 0
        messages.success(self.request, 'The goal was created successfully.')
        return super(GoalCreate,self).form_valid(form)

class GoalDelete(UserPassesTestMixin, generic.edit.DeleteView):
    model = Goal
    success_url = reverse_lazy('goals')
    template_name = "admin/confirm_delete.html"

    def test_func(self):
        goal = Goal.objects.get(pk = self.kwargs['pk'])
        return self.request.user == goal.creator

class GoalListView(generic.ListView):
    model       = Goal
    paginate_by = 10

    def get_queryset(self):
        return Goal.objects.all() \
                .annotate(num_sociables=Count('sociable')) \
                .order_by('-num_sociables')

class GoalDetailView(generic.DetailView):
    model = Goal