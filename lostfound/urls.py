from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse

def root_view(request):
    return JsonResponse({
        'message': 'Lost & Found API',
        'endpoints': {
            'items': '/api/items/',
            'admin': '/admin/',
        }
    })

urlpatterns = [
    path('', root_view, name='root'),
    path('admin/', admin.site.urls),
    path('api/items/', include('items.urls')),
]

if settings.DEBUG:
    # Serve media files during development. When deploying to production, it's
    # recommended to let the webserver (NGINX, Render static storage, etc.) serve
    # media files and to disable this in production. For local development we
    # mount the media URL so the app can load images from the `media/` dir.
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
