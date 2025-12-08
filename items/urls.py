from django.urls import path
from .views import (
    LostItemListCreateView,
    register,
    login,
    LostItemDetailView,
    MessageListCreateView,
    admin_login,
    whoami,
    contact_admin,
    conversations,
    health_superuser,
    health_db,
)

urlpatterns = [
    path('', LostItemListCreateView.as_view(), name='item-list-create'),
    path('register/', register, name='register'),
    path('login/', login, name='login'),
    path('<int:pk>/', LostItemDetailView.as_view(), name='item-detail'),
    # Chat endpoints
    path('messages/', MessageListCreateView.as_view(), name='messages-list-create'),
    path('admin_login/', admin_login, name='admin-login'),
    path('whoami/', whoami, name='whoami'),
    path('contact_admin/', contact_admin, name='contact-admin'),
    path('conversations/', conversations, name='conversations'),
    path('health/superuser/', health_superuser, name='health-superuser'),
    path('health/db/', health_db, name='health-db'),
]
