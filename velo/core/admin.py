# -*- coding: utf-8 -*-
from __future__ import unicode_literals, absolute_import, division, print_function

from django.conf import settings
from django.contrib import admin
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.admin import UserAdmin
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django import forms

from mptt.admin import MPTTModelAdmin
# from social.apps.django_app.default.models import UserSocialAuth

from velo.core.models import User, Choices, Competition, Distance, InsuranceCompany, Insurance, CustomSlug, Log, Map


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("email",)

    def clean_email(self):
        # Since User.username is unique, this check is redundant,
        # but it sets a nicer error message than the ORM. See #13147.
        email = self.cleaned_data["email"]
        try:
            User._default_manager.get(email=email)
        except User.DoesNotExist:
            return email
        raise forms.ValidationError(self.error_messages['duplicate_email'])


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = "__all__"

#
# class SocialInline(admin.TabularInline):
#     model = UserSocialAuth
#     extra = 0


class CustomUserAdmin(UserAdmin):
    # inlines = (SocialInline,)
    filter_horizontal = ('groups', 'user_permissions',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'ssn', 'birthday')}),
        (_('Contact information'), {'fields': ('country', 'city', 'bike_brand', 'phone_number',)}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Newsletters'), {'fields': ('send_email',)}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    list_display = ('email', 'first_name', 'last_name', 'is_staff')
    search_fields = ('first_name', 'last_name', 'email')
    ordering = ('email',)
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm


admin.site.register(User, CustomUserAdmin)


class ChoicesAdmin(admin.ModelAdmin):
    list_filter = ('kind',)
    list_display = ('__str__', 'kind', 'is_active')


class MapAdmin(admin.ModelAdmin):
    list_filter = ('competition',)
    list_display = ('__str__', 'ordering', 'competition', 'parent_competition')


admin.site.register(Choices, ChoicesAdmin)


class CustomMPTTModelAdmin(MPTTModelAdmin):
    mptt_level_indent = 20


admin.site.register(Competition, CustomMPTTModelAdmin)
admin.site.register(Distance)

admin.site.register(InsuranceCompany)
admin.site.register(Insurance)

admin.site.register(CustomSlug)
admin.site.register(Log)

admin.site.register(Map, MapAdmin)


def admin_login(request, extra_context=None):
    return HttpResponseRedirect(reverse(settings.LOGIN_URL))


admin.site.login = admin_login
