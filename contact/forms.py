from django.template import loader
from django.forms import ModelForm, widgets
from common.tasks import notify_admins
from .models import Contact


class ContactForm(ModelForm):
    def send_admin_notification(self):
        name = self.cleaned_data['name']
        message = self.cleaned_data['message']
        body = loader.render_to_string(
            'contact/contact_email.html',
            {'name': name, 'message': message}
        )
        notify_admins.delay(
            subject=f'New contact from {name}',
            body=body
        )

    class Meta:
        model = Contact
        exclude = ('date',)
        widgets = {
            'subject': widgets.Select(),
            'phone': widgets.Input(attrs={'placeholder': '(555) 555-5555'}),
            'message': widgets.Textarea(attrs={'rows': 5})
        }
