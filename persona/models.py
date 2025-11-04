import os
import uuid
from django.db import models
from django.urls import reverse

def persona_portrait_path(instance, filename):
    """Upload path voor persona portretten"""
    ext = filename.split('.')[-1]
    filename = f"portrait_{uuid.uuid4().hex}.{ext}"
    return os.path.join('persona/portraits/', filename)

class Persona(models.Model):
    """Model representing a passer-by persona on the street."""
    title = models.CharField(max_length=200)
    description = models.TextField()
    core_question = models.TextField()
    portrait = models.ImageField(
        upload_to=persona_portrait_path,
        blank=True,
        null=True,
        verbose_name="Portret foto"
    )
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        """Persona is represented by its title."""
        return str(self.title)
    
    def get_absolute_url(self):
        """Returns the url to access a particular persona instance."""
        return reverse('persona-detail', kwargs={'pk': self.pk})
    
    @property
    def portrait_url(self):
        """Returns the URL of the portrait image or a default image if none is set."""
        if self.portrait and hasattr(self.portrait, 'url'):
            return self.portrait.url
        return '/static/persona/images/empty_portrait.jpg'

class Problem(models.Model):
    """Model representing a problem faced by passer-by."""
    persona = models.ForeignKey(Persona, on_delete=models.CASCADE, related_name='problems')
    description = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Problems are ordered by most recent first."""
        ordering = ['-date_created']

    def __str__(self):
        """Problem is represented by its persona title and the first 50 chars of its description."""
        return f"{self.persona.title} - {self.description[:50]}..."

class Reaction(models.Model):
    """Model representing a reaction you can get from a passer-by"""
    persona = models.ForeignKey(Persona, on_delete=models.CASCADE, related_name='reactions')
    description = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        """Reactions are ordered by most recent first."""
        ordering = ['-date_created']

    def __str__(self):
        return f"{self.persona.title} - {self.description[:50]}..."
