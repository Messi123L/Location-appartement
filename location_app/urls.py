from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core import views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Pages principales
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    
    # Appartements
    path('apartments/', views.apartment_list, name='apartment_list'),
    path('apartments/<int:pk>/', views.apartment_detail, name='apartment_detail'),
    path('apartments/create/', views.apartment_create, name='apartment_create'),
    path('apartments/<int:pk>/update/', views.apartment_update, name='apartment_update'),
    path('apartments/<int:pk>/delete/', views.apartment_delete, name='apartment_delete'),
    
    # Réservations
    path('reservations/', views.reservation_history, name='reservation_history'),
    path('reservations/<int:pk>/', views.reservation_detail, name='reservation_detail'),
    path('reservations/<int:pk>/cancel/', views.reservation_cancel, name='reservation_cancel'),
    path('apartments/<int:apartment_pk>/reserve/', views.reservation_create, name='reservation_create'),
    
    # Messages
    path('messages/', views.message_list, name='message_list'),
    path('messages/new/', views.message_create, name='message_create'),
    path('messages/to/<int:receiver_id>/', views.message_create, name='message_create_to'),
    
    # Notifications
    path('notifications/', views.notification_list, name='notification_list'),
]

# Gestion des fichiers médias en développement
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
