import base64
import time

from django.db import IntegrityError
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect, render_to_response
from django.template.response import SimpleTemplateResponse
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.generic import TemplateView

from .models import EmailBlacklist


class SitemapView(TemplateView):
    template_name = 'sitemap.html'


##
#
#  Error Handler Views
#
##
@xframe_options_exempt
def error404(request):
    return render_to_response('404.html', {
        'STATIC_URL': getattr(settings, 'STATIC_URL', '/static/'),
    })


@xframe_options_exempt
def error500(request):
    return render_to_response('500.html', {
        'STATIC_URL': getattr(settings, 'STATIC_URL', '/static/'),
    })


@login_required(
    login_url=getattr(
        settings, 'ROOT_INFO_REDIRECT',
        getattr(settings, 'LOGIN_URL', '/login')
    ),
    redirect_field_name=None
)
def info_view(request):
    return redirect(getattr(settings, 'LOGIN_REDIRECT_URL'))


def email_unsubscribe(request, *args, **kwargs):
    if time.time() > int(kwargs['expiration']):
        return HttpResponse('Your unsubscription link has expired.')

    try:
        email = base64.b64decode(kwargs['email_encoded'])
    except TypeError:
        return HttpResponse('Invalid unsubscribe link.')

    if not EmailBlacklist.verify_email_signature(**kwargs):
        return HttpResponse('Invalid unsubscribe link.')

    blacklist_instance = EmailBlacklist(email=email)
    try:
        blacklist_instance.save()
    except IntegrityError:
        pass

    return HttpResponse("You will no longer receive email notifications for \
                        earned badges from this domain.")
