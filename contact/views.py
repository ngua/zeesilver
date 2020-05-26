from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.messages.views import SuccessMessageMixin
from django.utils.decorators import method_decorator
from honeypot.decorators import check_honeypot
from .forms import ContactForm


@method_decorator(check_honeypot, name='dispatch')
class ContactCreateView(SuccessMessageMixin, CreateView):
    form_class = ContactForm
    template_name = 'contact/contact.html'
    success_url = reverse_lazy('index')
    success_message = (
        'Thanks for reaching out, %(name)s! '
        "We'll get back to you soon."
    )

    def form_valid(self, form):
        form.save()
        form.send_admin_notification()
        response = super().form_valid(form)
        return response
