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

    def clean(self):
        cleaned_data = super().clean()
        q = cleaned_data.get('q')

        if not q:
            raise forms.ValidationError(
                'No value'
            )
