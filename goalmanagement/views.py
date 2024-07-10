from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views import generic
from django.contrib import messages
from django.urls import reverse_lazy
from django.db.models import Count
from .models import Goal


class GoalCreate(LoginRequiredMixin, generic.edit.CreateView):
    '''Generic editing view to create Goal:
    https://docs.djangoproject.com/en/5.0/ref/class-based-views/generic-editing/'''
    model       = Goal
    fields      = ['title']
    success_url = reverse_lazy('goals')

    def form_valid(self, form):
        form.instance.creator   = self.request.user
        messages.success(self.request, 'The goal was created successfully.')
        return super(GoalCreate,self).form_valid(form)


class GoalDelete(UserPassesTestMixin, generic.edit.DeleteView):
    '''Generic editing view to delete goal:
    https://docs.djangoproject.com/en/5.0/ref/class-based-views/generic-editing/'''
    model = Goal
    success_url = reverse_lazy('goals')
    template_name = "admin/confirm_delete.html"

    def test_func(self):
        goal = Goal.objects.get(pk = self.kwargs['pk'])
        return self.request.user == goal.creator


class GoalListView(generic.ListView):
    '''Generic display view to show an overview of Goal:
    https://docs.djangoproject.com/en/5.0/ref/class-based-views/generic-display/'''
    model       = Goal
    paginate_by = 10

    def get_queryset(self):
        '''Goals are ordered py popularity, thus by how many times it is chosen for a sociable'''
        return Goal.objects.all() \
                .annotate(nr_sociables=Count('sociable')) \
                .order_by('-nr_sociables')


class GoalDetailView(generic.DetailView):
    '''Generic display view to get the detailpage of Goal:
    https://docs.djangoproject.com/en/5.0/ref/class-based-views/generic-display/'''
    model = Goal
