from django.forms import ModelForm, widgets
from .tasks import mail_admins_task
from .models import Contact


class ContactForm(ModelForm):
    def send_admin_notification(self):
        name = self.cleaned_data['name']
        message = self.cleaned_data['message']
        mail_admins_task.delay(
            subject=f'New contact from {name}',
            message=message
        )

    class Meta:
        model = Contact
        exclude = ('date',)
        widgets = {
            'subject': widgets.Select(),
            'phone': widgets.Input(attrs={'placeholder': '(555) 555-5555'}),
            'message': widgets.Textarea(attrs={'rows': 5})
        }
