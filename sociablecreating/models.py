from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class Sociable(models.Model):
    """The object that is passed from person to person"""

    slug         = models.SlugField(
        verbose_name="Code om de sociable te kunnen vinden",
        max_length=8,
        unique=True,
        editable=False,
    )
    owner        = models.ForeignKey(User, on_delete=models.CASCADE)
    date_created = models.DateTimeField(
        auto_now_add=True, verbose_name="Datum aangemaakt"
    )

    class Meta:
        """Order descending"""

        ordering = ["-date_created"]

    def get_absolute_url(self):
        """Given the slug of the sociable,
        returns the url with the slug appended after,
        so that sociablepage is findable by the reciever of the sociable"""
        return reverse("sociable", kwargs={"slug": self.slug})

    def __str__(self):
        return str(self.slug)


class LogMessage(models.Model):
    """The message the receiver of the sociable leaves on the sociable page"""

    sociable = models.ForeignKey(Sociable, on_delete=models.CASCADE)
    author   = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    name     = models.CharField(
        max_length=70,
        default="Anoniem",
        verbose_name="Je naam",
        help_text="Een naam geeft al context aan een bericht. Voel je ook vrij om je naam op anoniem te houden",
    )
    body     = models.TextField(
        max_length=30000,
        verbose_name="Bericht",
        help_text="Schrijf over je ervaringen van het contact. Voel je vrij te delen wat je wel en niet wilt delen.",
    )
    date_created = models.DateTimeField(
        auto_now_add=True, verbose_name="Datum aangemaakt"
    )
    date_changed = models.DateTimeField(verbose_name="Datum bewerkt", null=True)
    is_read      = models.BooleanField(verbose_name="is gelezen", default=False)

    class Meta:
        """Order logmessages in descending order by date created"""
        ordering = ["-date_created"]

    def __str__(self):
        return str(self.body[0:50] + " . . .")

    def get_absolute_url(self):
        """After entering a message,
        the visitor is redirected towards the sociable page"""
        return reverse("sociable", kwargs={"slug": self.sociable.slug})
