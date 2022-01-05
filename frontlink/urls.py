from django.urls import re_path
from .conf import settings
from django.views.static import serve

urlpatterns = [
    re_path(r'^%s(?P<path>.*)$' % settings.FRONTEND_URL,
            serve, {'document_root': settings.FRONTEND_ROOT}),
]
    