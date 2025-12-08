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
    # Serve media files. On Render, there's no separate web server; small apps
    # can serve media directly from Django.
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
