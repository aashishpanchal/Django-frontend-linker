from django.apps import apps
from django.conf import settings as django_settings
from django.test.signals import setting_changed
from django.utils.functional import LazyObject
from django.utils.module_loading import import_string

FRONTEND_LINKER_NAMESPACE = "FRONTEND_LINKER"

WarningMessage = """
    Please add the following to your settings.py:

    FRONTEND_LINKER = {
        FRONTEND_ROOT: BASE_DIR / '%s',
    }
"""

STATIC_NAME = 'build_staticfiles'

DEFAULTS = {
    'FRONTEND_ROOT': django_settings.BASE_DIR / STATIC_NAME,
    'FRONTEND_URL': '',
}


class Settings:
    def __init__(self, default_settings, explicit_overriden_settings: dict = None):
        if explicit_overriden_settings is None:
            explicit_overriden_settings = {}

        overriden_settings = (
            getattr(django_settings, FRONTEND_LINKER_NAMESPACE, {})
            or explicit_overriden_settings
        )

        self._load_default_settings()
        self._override_settings(overriden_settings)

    def _load_default_settings(self):
        for setting_name, setting_value in DEFAULTS.items():
            if setting_name.isupper():
                setattr(self, setting_name, setting_value)

    def _override_settings(self, overriden_settings: dict):
        for setting_name, setting_value in overriden_settings.items():
            value = setting_value
            if isinstance(setting_value, dict):
                value = getattr(self, setting_name, {})
            setattr(self, setting_name, value)


class LazySettings(LazyObject):
    def _setup(self, explicit_overriden_settings=None):
        self._wrapped = Settings(DEFAULTS, explicit_overriden_settings)


settings = LazySettings()


def reload_settings(*args, **kwargs):
    global settings
    setting, value = kwargs["setting"], kwargs["value"]
    if setting == FRONTEND_LINKER_NAMESPACE:
        settings._setup(explicit_overriden_settings=value)


setting_changed.connect(reload_settings)
