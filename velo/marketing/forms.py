import requests
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit
from django import forms
from django.conf import settings


class SendyCreateForm(forms.Form):
    template = forms.ChoiceField(required=False, choices=())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        templates = requests.get("https://us13.api.mailchimp.com/3.0/templates", params={"type": "user"}, auth=("user", settings.MC_APIKEY)).json()
        self.fields['template'].choices = [(template.get('id'), template.get('name')) for template in templates.get('templates')]

        self.helper = FormHelper()
        self.helper.form_tag = True
        # self.helper.
        self.helper.layout = Layout(
            Row(
                Column(
                    'template',
                    Submit('submit', 'Izveidot'),
                    css_class='col-sm-4',
                )
            ),
        )
