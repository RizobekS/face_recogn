from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from .i18n import ActivateLanguageView
from apps.face.views import face_check_in, verify_face

urlpatterns = [
                  path("set_language/<str:lang>/",
                       ActivateLanguageView.as_view(), name="set_language_from_url"),
                  path('i18n/', include('django.conf.urls.i18n')),
                  path('admin/', admin.site.urls),
                  path('ckeditor/', include('ckeditor_uploader.urls')),
                  path('verify-face/', verify_face, name='verify_face'),
              ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) \
              + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += i18n_patterns(
    path('', include('apps.face.urls', namespace='registration')),
    prefix_default_language=True,
)
