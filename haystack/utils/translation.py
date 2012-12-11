from django.conf import settings
from django.utils.translation import (ugettext_lazy, get_language, activate,
                                      string_concat)

def proxy_name(model, language_code):
    safe_code = language_code.replace('-', ' ').title().replace(' ', '_')
    return '%s_%s' % (model.__name__, safe_code)


def proxy_factory(model, language_code, language_name):
    def get_absolute_url(self):
        if len(settings.LANGUAGES) > 1:
            old_language = get_language()
            try:
                activate(language_code)
                return '/%s%s' % (language_code, model.get_absolute_url(self))
            finally:
                activate(old_language)
        else:
            return model.get_absolute_url(self)

    class Meta:
        proxy = True
        app_label = 'haystack'
        if len(settings.LANGUAGES) > 1:
            verbose_name = string_concat(model._meta.verbose_name,
                                         ' (', language_name, ')')
            verbose_name_plural = string_concat(model._meta.verbose_name_plural,
                                                ' (', language_name, ')')
        else:
            verbose_name = model._meta.verbose_name
            verbose_name_plural = model._meta.verbose_name_plural

    attrs = {'__module__': model.__module__,
             'Meta': Meta,
             'objects': model.objects.__class__(),
             'get_absolute_url': get_absolute_url}

    _Proxy = type(proxy_name(model, language_code), (model,), attrs)

    return _Proxy

def create_proxies(model, namespace):
    for language_code, language_name in settings.LANGUAGES:
        if isinstance(language_name, basestring):
            language_name = ugettext_lazy(language_name)
        proxy_model = proxy_factory(model, language_code, language_name)
        namespace[proxy_model.__name__] = proxy_model
    return namespace
