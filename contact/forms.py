from django.forms import ModelForm, widgets
from .models import Contact


class ContactForm(ModelForm):
    class Meta:
        model = Contact
        exclude = ('date',)
        widgets = {
            'subject': widgets.Select(),
            'phone': widgets.Input(attrs={'placeholder': '(555) 555-5555'}),
            'message': widgets.Textarea(attrs={'rows': 5})
        }
