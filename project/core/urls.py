# coding=utf-8
from __future__ import unicode_literals  # u'' strings by default # Awesome :)
from django.conf.urls import patterns, url
from django.core.urlresolvers import reverse_lazy
from core.forms import PasswordResetForm, SetPasswordFormCustom, AuthenticationFormCustom
from core.views import UserRegistrationView, UserEmailConfirm, ChangeEmailView, ChangePasswordView, ProfileView, \
    ResendEmailView
from django.utils.translation import ugettext_lazy as _
from payment.views import TeamPayView
from registration.views import MyApplicationList
from team.views import MyTeamList, TeamCreateView, TeamUpdateView, TeamApplyList, TeamApply

urlpatterns = patterns('',
                       url(_(r'^register/$'), UserRegistrationView.as_view(), name="register"),
                       url(_(r'^register/email/$'), 'core.views.new_user_email_view', name="register_user_email"),


                       url(_(
                           r'^email/confirm/(?P<slug>[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})/$'),
                           UserEmailConfirm.as_view(), name='email_confirmation_view'),
                       url(_(r'^email/$'), ChangeEmailView.as_view(), name='email_change_view'),
                       url(_(r'^email/resend/$'), ResendEmailView.as_view(), name='email_resend_view'),
                       url(_(r'^password_change/$'), ChangePasswordView.as_view(), name='password_change'),
                       url(_(r'^login/$'), 'core.views.login', name='login',
                           kwargs={'authentication_form': AuthenticationFormCustom}),
                       url(_(r'^logout/$'), 'django.contrib.auth.views.logout', {'next_page': '/'}, name='logout'),
                       url(_(r'^profile/$'), ProfileView.as_view(), name='profile'),

                       url(_(r'^password_reset/$'), 'django.contrib.auth.views.password_reset', name='password_reset',
                           kwargs={'post_reset_redirect': reverse_lazy('accounts:password_reset_done'),
                                   'template_name': 'registration/password_reset_form_velo.html',
                                   'password_reset_form': PasswordResetForm}),
                       url(_(r'^password_reset/done/$'), 'django.contrib.auth.views.password_reset_done',
                           name='password_reset_done',
                           kwargs={'template_name': 'registration/password_reset_done_velo.html'}),
                       # Support old style base36 password reset links; remove in Django 1.7
                       url(_(r'^reset/(?P<uidb36>[0-9A-Za-z]{1,13})-(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$'),
                           'django.contrib.auth.views.password_reset_confirm_uidb36', kwargs={
                               'post_reset_redirect': reverse_lazy('accounts:password_reset_complete')
                           }),
                       url(_(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$'),
                           'django.contrib.auth.views.password_reset_confirm',
                           name='password_reset_confirm', kwargs={
                               'post_reset_redirect': reverse_lazy('accounts:password_reset_complete'),
                               'template_name': 'registration/password_reset_confirm_velo.html',
                               'set_password_form': SetPasswordFormCustom,
                           }),
                       url(_(r'^reset/done/$'), 'django.contrib.auth.views.password_reset_complete',
                           name='password_reset_complete', kwargs={
                               'template_name': 'registration/password_reset_complete_velo.html',
                           }),

                       url(_(r'^my_applications/$'), MyApplicationList.as_view(), name='applications'),
                       url(_(r'^my_team/$'), MyTeamList.as_view(), name='team_list'),
                       url(_(r'^my_team/add/$'), TeamCreateView.as_view(), name='team'),
                       url(_(r'^my_team/(?P<pk2>\d+)/$'), TeamUpdateView.as_view(), name='team'),

                       url(_(r'^my_team/(?P<pk2>\d+)/pay/$'), TeamPayView.as_view(), name='team_pay'),

                       url(_(r'^my_team/(?P<pk2>\d+)/apply/$'), TeamApplyList.as_view(), name='team_apply_list'),
                       url(_(r'^my_team/(?P<pk2>\d+)/apply/(?P<competition_pk>\d+)/$'), TeamApply.as_view(),
                           name='team_apply_list'),

)