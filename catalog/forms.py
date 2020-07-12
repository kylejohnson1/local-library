import datetime

from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

from catalog.models import Language, Genre

class RenewBookForm(forms.Form):
    renewal_date = forms.DateField(help_text="Enter a date between now and 4 weeks (default 3).")

    def clean_renewal_date(self):
        data = self.cleaned_data['renewal_date']

        # Check if a date is not in the past
        if data < datetime.date.today():
            raise ValidationError(_('Invalid date - renewal in past'))

        # Check it a date is in the allowed range (+4 weeks from today)
        if data > datetime.date.today() + datetime.timedelta(weeks=4):
            raise ValidationError(_('Invalid date - renewal more than 4 weeks ahead'))

        return data

class BookFilterForm(forms.Form):
    title_contains = forms.CharField(label='Title contains', max_length=100, required=False)
    author_contains = forms.CharField(label='Author contains', max_length=100, required=False)

    LANGUAGE_CHOICES = [(language.name, language.name) for language in Language.objects.all()]
    LANGUAGE_CHOICES.insert(0, ('any','Any'))

    language = forms.ChoiceField(choices=LANGUAGE_CHOICES, initial='any', required=False)

    GENRE_CHOICES = [(genre.name, genre.name) for genre in Genre.objects.all()]
    GENRE_CHOICES.insert(0, ('any','Any'))

    genre = forms.ChoiceField(choices=GENRE_CHOICES, initial='any', required=False)

    ORDER_BY_CHOICES = [
        ('title', 'Title'),
        ('author', 'Author'),
        ('language', 'Language')
    ]

    order_by = forms.ChoiceField(choices=ORDER_BY_CHOICES, required=False)
    
