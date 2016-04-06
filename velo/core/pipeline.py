from django.shortcuts import redirect
import pwgen

from social.pipeline.partial import partial
from social.pipeline.user import USER_FIELDS
from velo.core.models import User


@partial
def require_email(strategy, details, user=None, is_new=False, *args, **kwargs):
    if kwargs.get('ajax') or user and user.email:
        return
    elif is_new:
        if not details.get('email'):
            email = strategy.request.session.get('partial_email')
            if email:
                details['email'] = email
            else:
                return redirect('accounts:register_user_email')
        else:
            try:
                User.objects.get(email=details.get('email'))
                details['email'] = ''  # User with such email exists.
                return redirect('accounts:register_user_email')
            except:
                pass


def create_user(strategy, details, user=None, *args, **kwargs):
    if user:
        return {'is_new': False}

    fields = dict((name, kwargs.get(name) or details.get(name))
                        for name in strategy.setting('USER_FIELDS',
                                                      USER_FIELDS))
    if not fields:
        return

    user = User.objects.create(password='!', **fields)
    user.set_password(pwgen.pwgen())
    user.save()

    return {
        'is_new': True,
        'user': user,
    }
