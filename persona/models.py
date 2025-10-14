from django.db import models
from django.urls import reverse

class Persona(models.Model):
    """Model representing a passer-by persona on the street."""
    title = models.CharField(max_length=200)
    description = models.TextField()
    core_question = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        """Persona is represented by its title."""
        return str(self.title)
    
    def get_absolute_url(self):
        """Returns the url to access a particular persona instance."""
        return reverse('persona-detail', kwargs={'pk': self.pk})

class Problem(models.Model):
    """Model representing a problem faced by passer-by."""
    persona = models.ForeignKey(Persona, on_delete=models.CASCADE, related_name='problems')
    text = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Problems are ordered by most recent first."""
        ordering = ['-date_added']

    def __str__(self):
        """Problem is represented by its persona title and the first 50 chars of its text."""
        return f"{self.persona.title} - {self.text[:50]}..."

class Reaction(models.Model):
    """Model representing a reaction you can get from a passer-by"""
    persona = models.ForeignKey(Persona, on_delete=models.CASCADE, related_name='reactions')
    text = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Reactions are ordered by most recent first."""
        ordering = ['-date_added']

    def __str__(self):
        return f"{self.persona.title} - {self.text[:50]}..."
