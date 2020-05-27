from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Div
from localflavor.us.us_states import US_STATES
from localflavor.us.forms import USStateField
from .models import Order


class OrderForm(forms.ModelForm):
    # Override the form field generated from the model to exclude
    # territories, Armed Forces states, etc...
    state = USStateField(widget=forms.Select(choices=US_STATES))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        # Disable the form tag to include Honeypot field
        self.helper.form_tag = False
        self.helper.layout = Layout(
            Fieldset(
                '',  # No legend
                Div(
                    Div('first_name', css_class='col-md-4 mb-3'),
                    Div('last_name', css_class='col-md-4 mb-3'),
                    Div('email', css_class='col-md-4 mb-3'),
                    css_class='form-row'
                ),
                Div(
                    Div('phone', css_class='col-md-4 mb-3'),
                    Div('street_address', css_class='col-md-8 mb-3'),
                    css_class='form-row'
                ),
                Div(
                    Div('city', css_class='col-md-6 mb-3'),
                    Div('state', css_class='col-md-4 mb-3'),
                    Div('zip_code', css_class='col-md-2 mb-3'),
                    css_class='form-row'
                )
            )
        )

    class Meta:
        model = Order
        fields = [
            'first_name', 'last_name', 'email', 'phone', 'street_address',
            'city', 'state', 'zip_code'
        ]
