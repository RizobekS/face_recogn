from urllib.parse import urlparse

from django.http import HttpResponseRedirect
from django.urls import resolve, reverse
from django.utils.translation import activate
from django.views import View

from . import settings


class ActivateLanguageView(View):

    def get(self, request, lang, **kwargs):
        next_url = request.GET.get('next', '/')

        parsed_url = urlparse(next_url)
        if parsed_url.netloc:
            next_url = '/'

        try:
            match = resolve(parsed_url.path)
            new_path = reverse(match.view_name, kwargs=match.kwargs)

            new_path = new_path.replace(f'/{request.LANGUAGE_CODE}/', f'/{lang}/', 1)
            next_url = new_path
        except:
            pass

        activate(lang)
        response = HttpResponseRedirect(next_url)
        response.set_cookie(settings.LANGUAGE_COOKIE_NAME, lang)
        return response
