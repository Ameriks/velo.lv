# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, division, print_function

from django import forms
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from crispy_forms.layout import Layout, Row, Column, Field, Fieldset, HTML, Submit, Div
from crispy_forms.helper import FormHelper
import math
import datetime

from slugify import slugify

from velo.core.models import Distance, CustomSlug
from velo.team.models import Member, Team
from velo.velo.mixins.forms import RequestKwargModelFormMixin, GetClassNameMixin, CleanEmailMixin
from velo.velo.utils import bday_from_LV_SSN


class MemberInlineForm(RequestKwargModelFormMixin, forms.ModelForm):
    class Meta:
        model = Member
        fields = ('country', 'ssn', 'first_name', 'last_name', 'id', 'birthday', 'gender')

    def save(self, commit=True):
        obj = super(MemberInlineForm, self).save(commit=False)

        if not obj.id:
            obj.status = Member.STATUS_ACTIVE

        if commit:
            obj.save()
        return obj

    def clean_ssn(self):
        if self.instance.id and not self.request.user.has_perm('team.change_member'):
            return self.instance.ssn
        else:
            return self.cleaned_data.get('ssn', '').replace('-', '').replace(' ', '')

    def clean_birthday(self):
        if self.instance.id and not self.request.user.has_perm('team.change_member'):
            return self.instance.birthday
        else:
            if self.cleaned_data.get('country') == 'LV':
                ssn = self.cleaned_data.get('ssn', '')
                return bday_from_LV_SSN(ssn)
            else:
                return self.cleaned_data.get('birthday')

    def clean(self):
        cleaned_data = self.cleaned_data

        ssn = cleaned_data.get('ssn', '')
        country = cleaned_data.get('country')

        valid = True

        if country == 'LV':
            try:
                if not ssn or not len(ssn) == 11:
                    self._errors.update({'ssn': [_("Invalid Social Security Number."), ]})
                    valid = False
                checksum = 1
                for i in xrange(10):
                    checksum -= int(ssn[i]) * int("01060307091005080402"[i * 2:i * 2 + 2])
                if not int(checksum - math.floor(checksum / 11) * 11) == int(ssn[10]):
                    self._errors.update({'ssn': [_("Invalid Social Security Number."), ]})
                    valid = False
            except:
                self._errors.update({'ssn': [_("Invalid Social Security Number."), ]})
                valid = False

            if valid:
                try:
                    member = Member.objects.exclude(id=self.instance.id).filter(status=Member.STATUS_ACTIVE).get(
                        team__distance__competition_id=self.instance.team.distance.competition_id, ssn=ssn)
                    self._errors.update({
                        'ssn': [
                            _("Member with his SSN is already registered in other team - {0}.").format(member.team), ]})
                except:
                    pass
        else:
            try:
                slug = CustomSlug.objects.get(first_name=cleaned_data.get('first_name', ''),
                                              last_name=cleaned_data.get('last_name', ''),
                                              birthday=cleaned_data.get('birthday', '')).slug
            except CustomSlug.DoesNotExist:
                slug = slugify('%s-%s-%i' % (cleaned_data.get('first_name', ''), cleaned_data.get('last_name', ''),
                                             cleaned_data.get('birthday', '').year), only_ascii=True)

            try:
                member = Member.objects.exclude(id=self.instance.id).filter(status=Member.STATUS_ACTIVE).get(
                    team__distance__competition_id=self.instance.team.distance.competition_id, slug=slug)
                self._errors.update({'ssn': [
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

    def __init__(self, *args, **kwargs):
        super(MemberInlineForm, self).__init__(*args, **kwargs)

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
            self.fields['ssn'].widget.attrs['readonly'] = True
            self.fields['country'].widget.attrs['readonly'] = True
            self.fields['birthday'].widget.attrs['readonly'] = True
            self.fields['gender'].widget.attrs['readonly'] = True

        self.helper = FormHelper()
        self.helper.form_tag = False
        self.helper.template = "bootstrap/velo_whole_uni_formset.html"
        self.helper.layout = Layout(
            Row(
                Column(
                    Row(
                        Column('first_name', css_class='col-xs-6 col-sm-2'),
                        Column('last_name', css_class='col-xs-6 col-sm-3'),
                        Column('gender', css_class='col-xs-6 col-sm-2'),
                        Column('country', css_class='col-xs-6 col-sm-2'),
                        Column('ssn', css_class='col-xs-6 col-sm-3'),
                        Column('birthday', css_class='col-xs-6 col-sm-3'),
                    ),
                    'id',
                    Div(
                        Field('DELETE', ),
                        css_class='hidden',
                    ),
                    css_class='col-sm-12'
                ),
            ),
        )


class TeamForm(GetClassNameMixin, CleanEmailMixin, RequestKwargModelFormMixin, forms.ModelForm):
    class Meta:
        model = Team
        fields = (
            'distance', 'title', 'description', 'img', 'shirt_image', 'country', 'contact_person', 'email',
            'phone_number',
            'management_info',)

    class Media:
        js = ('js/jquery.formset.js', 'plugins/datepicker/bootstrap-datepicker.min.js',
              'plugins/jquery.maskedinput.js', 'plugins/mailgun_validator.js',
              'plugins/typeahead.js/typeahead.bundle.min.js')
        css = {
            'all': ('plugins/datepicker/datepicker.css',)
        }

    def clean_distance(self):
        distance = self.cleaned_data.get('distance')
        if self.instance.id:
            return self.instance.distance
        else:
            return distance

    def clean_title(self):
        title = self.cleaned_data.get('title')
        try:
            Team.objects.exclude(id=self.instance.id).get(slug=slugify(title),
                                                          distance__competition=self.cleaned_data.get(
                                                              'distance').competition)
        except Team.DoesNotExist:
            return title
        except AttributeError:
            return title
        raise forms.ValidationError(_("Team with such title already exist."), )

    def save(self, commit=True):
        obj = super(TeamForm, self).save(commit=False)

        if not obj.id:
            obj.owner = self.request.user
            obj.created_by = self.request.user
        else:
            obj.modified_by = self.request.user

        if commit:
            obj.save()
        return obj

    def __init__(self, *args, **kwargs):
        super(TeamForm, self).__init__(*args, **kwargs)
        self.fields['email'].required = True

        self.fields['country'].initial = 'LV'

        distances = Distance.objects.filter(can_have_teams=True, competition__is_in_menu=True).exclude(
            competition__competition_date__lt=timezone.now())
        self.fields['distance'].choices = [('', '------')] + [
            (str(distance.id), "{0} - {1}".format(distance.competition.__unicode__(), distance.__unicode__())) for
            distance in distances]

        try:
            if self.instance.distance not in distances:
                distance = self.instance.distance
                self.fields['distance'].choices.append((
                    str(distance.id),
                    "{0} - {1}".format(distance.competition.__unicode__(), distance.__unicode__())))
        except Distance.DoesNotExist:
            pass

        if self.instance.id:
            self.fields['distance'].widget.attrs['readonly'] = True

        try:
            next_competition = None
            competition = self.instance.distance.competition
            if competition.get_root().id == 1:
                next_competition = self.instance.distance.competition.children.filter(
                    competition_date__gt=timezone.now())[:1]
            elif competition.competition_date and competition.competition_date > datetime.date.today():
                next_competition = [competition, ]
            if next_competition and not self.request.user.has_perm('team.change_member'):
                next_competition = next_competition[0]
                button = Submit('submit_pay', _('Pay for %s') % next_competition)
            else:
                button = HTML('')
        except:
            button = HTML('')

        self.helper = FormHelper()
        self.helper.form_tag = True
        self.helper.layout = Layout(
            Row(
                Column(
                    'distance',
                    'title',
                    'country',
                    'description',
                    'img',
                    css_class='col-sm-6'
                ),
                Column(
                    'contact_person',
                    'email',
                    'phone_number',
                    'management_info',
                    'shirt_image',
                    css_class='col-sm-6'
                ),
            ),
            Row(
                Column(
                    Fieldset(
                        'Dalībnieki',
                        HTML('{% load crispy_forms_tags %}{% crispy member member.form.helper %}'),
                    ),
                    css_class='col-xs-12'
                )
            ),
            Row(
                Column(Submit('submit', _('Save')), css_class='col-sm-2'),
                Column(button, css_class='col-sm-2 pull-right'),
            ),
        )
