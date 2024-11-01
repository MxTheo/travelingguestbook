from django.db import models


class Feeling(models.Model):
    '''Feeling that user fills in at
    "hierdoor voelde ik mij [feeling]"'''

    name = models.CharField(
        max_length=50,
        null=False,
        verbose_name="Gevoel",
        help_text="Gevoel volgens geweldloze communicatie, waaruit de gebruiker kan kiezen voor het maken van een bericht",
    )
    category = models.ForeignKey(
        "nvc.Feeling",
        verbose_name="Categorie",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    isFullfilledNeed = models.BooleanField(
        verbose_name="is Gevoel bij vervulde behoefte?",
        help_text="Geweldloze communicatie deelt gevoelens in in gevoelens bij vervulde behoeften en gevoelens bij niet-vervulde behoeften. Is dit een gevoel bij een vervulde behoefte?",
        default=True,
    )

    def __str__(self):
        return self.name


class Need(models.Model):
    '''Need that user fills in at
    "omdat mijn behoefte aan [need] is vervuld"'''

    name = models.CharField(
        max_length=50,
        null=False,
        verbose_name="Behoefte",
        help_text="Behoefte volgens geweldloze communicatie, waaruit de gebruiker kan kiezen voor het maken van een bericht",
    )
    category = models.ForeignKey(
        "nvc.Need",
        verbose_name="Categorie",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    def __str__(self):
        return self.name
