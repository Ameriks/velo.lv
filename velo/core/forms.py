import datetime

from django import forms
from django.core.urlresolvers import reverse
from django.forms import Select
from django.utils.translation import ugettext, ugettext_lazy as _
from django.utils.safestring import mark_safe

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Div, Fieldset, Field
from django_countries.data import COUNTRIES

from velo.core.models import User, Choices
from velo.core.widgets import ButtonWidget, ProfileImage, SplitDateWidget


# NEW
class SignupForm(forms.Form):
    first_name = forms.CharField(max_length=30, label=_('First Name'), required=False)
    last_name = forms.CharField(max_length=30, label=_('Last Name'), required=False)
    send_email = forms.BooleanField(label=_('I want to receive newsletters'), required=False)
    birthday_day = forms.IntegerField(label=_('Birthday'), required=False)
    birthday_month = forms.IntegerField(label=_('Birthday'), required=False)
    birthday_year = forms.IntegerField(label=_('Birthday'), required=False)
    country = forms.ChoiceField(label=_('Country'), required=False, choices=sorted(COUNTRIES.items(), key=lambda tup: tup[1]))
    city = forms.ModelChoiceField(Choices.objects.filter(kind=Choices.KINDS.city), required=False, label=_('City'), empty_label=_("City"))
    bike_brand = forms.ModelChoiceField(Choices.objects.filter(kind=Choices.KINDS.bike_brand), required=False, label=_('Bike Brand'), empty_label=_("Bike Brand"))
    phone_number = forms.CharField(required=False, label=_('Phone number'))

    def __init__(self, *args, **kwargs):
        super(SignupForm, self).__init__(*args, **kwargs)
        self.fields['country'].initial = 'LV'

    def signup(self, request, user):
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.send_email = self.cleaned_data['send_email']
        user.country = self.cleaned_data['country']
        user.city = self.cleaned_data['city']
        user.bike_brand = self.cleaned_data['bike_brand']
        user.phone_number = self.cleaned_data['phone_number']
        try:
            user.birthday = datetime.date(self.cleaned_data['birthday_year'], self.cleaned_data['birthday_month'], self.cleaned_data['birthday_day'])
        except:
            print("WRONG DATE")

        user.save()


# Is this needed?
class UserProfileForm(forms.ModelForm):
    email = forms.CharField(required=False, widget=ButtonWidget())
    password = forms.CharField(required=False, widget=ButtonWidget())
    social = forms.CharField(required=False, widget=ButtonWidget())

    class Meta:
        model = User
        fields = ("first_name", "last_name", "country", "birthday", "city", "bike_brand", "phone_number", "send_email", "image", "description")
        widgets = {
            'image': ProfileImage,
            'birthday': SplitDateWidget
        }

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)

        self.fields['email'].widget.attrs.update(
            {'href': reverse('account_email'), 'class': 'btn btn--50 btn--dblue btn--blue-hover btn--blue-active w100'})
        self.fields['email'].widget.text = mark_safe(
            "%s <small>%s</small>" % (self.instance.email, ugettext('Change Email')))

        self.fields['password'].widget.attrs.update(
            {'href': reverse('account_change_password'), 'class': 'btn btn--50 btn--dblue btn--blue-hover btn--blue-active w100'})
        self.fields['password'].widget.text = mark_safe("****** <small>%s</small>" % ugettext('Change Password'))

        self.fields['social'].widget.attrs.update(
            {'href': reverse('socialaccount_connections'), 'class': 'btn btn--50 btn--dblue btn--blue-hover btn--blue-active w100'})
        self.fields['social'].widget.text = mark_safe(ugettext('Connect / Disconnect Social Accounts'))


        self.helper = FormHelper()
        self.helper.form_class = "w100 bottom-margin--20  js-form"
        self.helper.label_class = "w100 fs13 bottom-margin--10"
        self.helper.field_class = "input-field if--50 if--dark"
        self.helper.layout = Layout(
            Div(
                Div(
                    Div(css_class='w100 bottom-margin--20',),
                    Fieldset(
                        None,
                        'email',
                        'password',
                        Field('country', css_class="select-hide js-select select"),
                        Field('city', css_class="select-hide js-select select"),
                        Field('bike_brand', css_class="select-hide js-select select"),
                        'social',
                        css_class='inner'
                    ),
                  css_class='col-xl-9 col-m-24 layouts-profile-left'
                ),


                Div(
                    Div(css_class='w100 bottom-margin--20', ),
                    Fieldset(
                        None,
                        Div(
                            Div(
                                "image",
                                css_class="col-xl-8 col-s-18"
                            ),
                            Div(
                               Field("description", css_class="layouts-profile-textarea input-field if--50 if--dark input-field--textarea w100"),
                                css_class="col-xl-16 col-s-24"
                            ),
                            Div(
                                Field("first_name", css_class="input-field if--50 if--dark"),
                              css_class="col-xl-12 col-s-24"
                            ),
                            Div(
                                Field("last_name", css_class="input-field if--50 if--dark"),
                                css_class="col-xl-12 col-s-24"
                            ),
                            Div(
                                Div(
                                    Div(

                                    ),
                                    "birthday",
                                    css_class="input-wrap w100 bottom-margin--20"
                                ),

                                css_class="col-xl-12 col-s-24"
                            ),
                            Div(
                                Field("phone_number", css_class="input-field if--50 if--dark"),
                                css_class="col-xl-12 col-s-24"
                            ),
                            Div(
                                "send_email",
                                css_class="col-xl-24"
                            ),
                          css_class='row row--gutters-20'
                        ),
                        css_class='inner'
                    ),
                    css_class="col-xl-15 col-m-24 bgc-dgray relative"
                ),

                Div(
                    Div(
                        Div(
                            css_class="col-xl-18 col-m-14 col-s-24"
                        ),
                        Div(
                            Submit('update_profile', _('Update Profile'), css_class='btn btn--50 btn--blue btn--blue-hover btn--blue-active w100'),
                          css_class="col-xl-6 col-m-10 col-s-24"
                        ),
                        css_class="row"
                    ),
                    css_class="col-xl-24 border-top border-bottom"
                ),


                css_class='row',
            ),

        )
