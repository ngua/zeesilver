from django import forms


class SearchForm(forms.Form):
    q = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={
                'required': 'true',
                'type': 'search',
                'name': 'q',
                'placeholder': 'Search...'
            }
        ))
