from django import forms
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from crispy_forms.layout import Layout, Row, Column, Field, Fieldset, HTML, Submit, Div
from crispy_forms.helper import FormHelper
import math
import datetime

from slugify import slugify

from velo.core.models import Distance, CustomSlug
from velo.core.widgets import SplitDateWidget, ProfileImage
from velo.team.models import Member, Team
from velo.velo.mixins.forms import RequestKwargModelFormMixin, GetClassNameMixin, CleanEmailMixin
from velo.velo.utils import bday_from_LV_SSN


class MemberInlineForm(RequestKwargModelFormMixin, forms.ModelForm):
    class Meta:
        model = Member
        fields = ('country', 'first_name', 'last_name', 'id', 'birthday', 'gender', 'image', "phone_number")
        widgets = {
            'birthday': SplitDateWidget,
            'image': ProfileImage,
        }

    def save(self, commit=True):
        obj = super().save(commit=False)

        if not obj.id:
            obj.status = Member.STATUS_ACTIVE

        if commit:
            obj.save()
        return obj

    def clean_birthday(self):
        if self.instance.id and not self.request.user.has_perm('team.change_member'):
            return self.instance.birthday
        else:
            return self.cleaned_data.get('birthday')

    def clean(self):
        cleaned_data = self.cleaned_data

        try:
            slug = CustomSlug.objects.get(first_name=cleaned_data.get('first_name', ''),
                                          last_name=cleaned_data.get('last_name', ''),
                                          birthday=cleaned_data.get('birthday', '')).slug
        except CustomSlug.DoesNotExist:
            slug = slugify('%s-%s-%i' % (cleaned_data.get('first_name', ''), cleaned_data.get('last_name', ''),
                                         cleaned_data.get('birthday', timezone.now()).year), only_ascii=True)

        try:
            if "status" not in self.cleaned_data or self.cleaned_data.get("status") == Member.STATUS_ACTIVE:
                member = Member.objects.exclude(id=self.instance.id).filter(status=Member.STATUS_ACTIVE).get(team__distance__competition_id=self.instance.team.distance.competition_id,
                                                                                                             slug=slug,
                                                                                                             team__distance_id=self.instance.team.distance_id)
                self._errors.update({'first_name': [
                    _("Member with this First Name and Last Name is already registered in other team - {0}.").format(
                        member.team), ]})
        except:
            pass

        return cleaned_data

    def clean_first_name(self):
        if self.instance.id and not self.request.user.has_perm('team.change_member'):
            return self.instance.first_name
        else:
            return self.cleaned_data.get('first_name').strip().title()

    def clean_gender(self):
        if self.instance.id and not self.request.user.has_perm('team.change_member'):
            return self.instance.gender
        else:
            return self.cleaned_data.get('gender')

    def clean_last_name(self):
        if self.instance.id and not self.request.user.has_perm('team.change_member'):
            return self.instance.last_name
        else:
            return self.cleaned_data.get('last_name').strip().title()

    def clean_country(self):
        if self.instance.id and not self.request.user.has_perm('team.change_member'):
            return self.instance.country
        else:
            return self.cleaned_data.get('country')

    def clean_phone_number(self):
        if self.instance.id and not self.request.user.has_perm("team.change_member"):
            return self.instance.phone_number
        else:
            return self.cleaned_data.get("phone_number")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['country'].initial = 'LV'

        self.fields['country'].required = True
        self.fields['birthday'].required = True
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        self.fields['country'].required = True
        self.fields['gender'].required = True

        if self.instance.id and not self.request.user.has_perm('team.change_member'):
            self.fields['first_name'].widget.attrs['readonly'] = True
            self.fields['last_name'].widget.attrs['readonly'] = True
            self.fields['country'].widget.attrs['readonly'] = True
            self.fields['birthday'].widget.attrs['readonly'] = True
            self.fields['gender'].widget.attrs['readonly'] = True
            self.fields["phone_number"].widget.atrs["readonly"] = True

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.include_media = False
        self.helper.template = "team/form/member_inline.html"
        self.helper.layout = Layout()


class TeamForm(GetClassNameMixin, CleanEmailMixin, RequestKwargModelFormMixin, forms.ModelForm):
    class Meta:
        model = Team
        fields = (
            'distance', 'title', 'description', 'img', 'shirt_image', 'country', 'contact_person', 'email',
            'phone_number', 'is_w', 'management_info', 'show_contact_info')

    def clean_distance(self):
        distance = self.cleaned_data.get('distance')
        if self.instance.id:
            return self.instance.distance
        else:
            return distance

    def clean_title(self):
        title = self.cleaned_data.get('title')
        try:
            Team.objects.exclude(id=self.instance.id).get(slug=slugify(title), distance=self.cleaned_data.get('distance'))
        except Team.DoesNotExist:
            return title
        except AttributeError:
            return title
        raise forms.ValidationError(_("Team with such title already exist."), )

    def save(self, commit=True):
        obj = super().save(commit=False)

        if not obj.id:
            obj.owner = self.request.user
            obj.created_by = self.request.user
        else:
            obj.modified_by = self.request.user

        if commit:
            obj.save()
        return obj

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].required = True
        self.fields['is_w'].required = False
        self.fields['is_w'].label = "Sieviešu komanda?"

        self.fields['country'].initial = 'LV'

        distances = Distance.objects.filter(can_have_teams=True, competition__is_in_menu=True).exclude(
            competition__competition_date__lt=timezone.now()).order_by('competition_id', 'id')

        self.fields['distance'].choices = [('', '------')] + [
            (str(distance.id), "{0} - {1}".format(str(distance.competition), str(distance))) for
            distance in distances]

        if self.instance.distance_id:
            try:
                if self.instance.distance not in distances:
                    distance = self.instance.distance
                    self.fields['distance'].choices.append((
                        str(distance.id),
                        "{0} - {1}".format(str(distance.competition), str(distance))))
            except Distance.DoesNotExist:
                pass

        if self.instance.id:
            self.fields['distance'].widget.attrs['readonly'] = True
