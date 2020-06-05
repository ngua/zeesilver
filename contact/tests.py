from django.test import TestCase
from django.urls import reverse
from .forms import ContactForm
from .models import Contact


class ContactTestCase:
    def setUp(self):
        self.form_data = {
            'name': 'Test',
            'email': 'test@test.com',
            'subject': Contact.Subject.SALES,
            'message': 'A message',
            'phone': '',
            # Honeypot field
            'phonenumber': '',
        }


class ContactViewTestCase(ContactTestCase, TestCase):
    def test_get(self):
        response = self.client.get(reverse('contact'))
        self.assertEqual(response.status_code, 200)


class ContactFormTestCase(ContactTestCase, TestCase):
    def test_form_valid(self):
        data = self.form_data.copy()
        form = ContactForm(data)
        self.assertTrue(form.is_valid())
