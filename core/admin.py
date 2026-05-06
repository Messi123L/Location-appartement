from django.contrib import admin
from .models import User, Apartment, Reservation, Message, Notification

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role', 'is_active', 'date_joined')
    list_filter = ('role', 'is_active', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    fieldsets = (
        ('Informations de connexion', {
            'fields': ('username', 'password')
        }),
        ('Informations personnelles', {
            'fields': ('first_name', 'last_name', 'email', 'phone', 'avatar')
        }),
        ('Permissions', {
            'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Dates importantes', {
            'fields': ('last_login', 'date_joined')
        }),
    )


@admin.register(Apartment)
class ApartmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'city', 'owner', 'price_per_night', 'bedrooms', 'max_guests', 'is_validated', 'is_active')
    list_filter = ('city', 'is_validated', 'is_active', 'owner')
    search_fields = ('title', 'description', 'address', 'city')
    ordering = ('-created_at',)
    fieldsets = (
        ('Informations générales', {
            'fields': ('title', 'description', 'owner')
        }),
        ('Localisation', {
            'fields': ('address', 'city')
        }),
        ('Capacité et prix', {
            'fields': ('price_per_night', 'bedrooms', 'max_guests')
        }),
        ('Statut', {
            'fields': ('is_active', 'is_validated')
        }),
    )
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('apartment', 'client', 'check_in_date', 'check_out_date', 'number_of_guests', 'total_amount', 'status')
    list_filter = ('status', 'check_in_date', 'apartment')
    search_fields = ('apartment__title', 'client__username')
    ordering = ('-check_in_date',)
    fieldsets = (
        ('Informations de réservation', {
            'fields': ('apartment', 'client')
        }),
        ('Dates et capacité', {
            'fields': ('check_in_date', 'check_out_date', 'number_of_guests')
        }),
        ('Prix et statut', {
            'fields': ('total_amount', 'status')
        }),
    )
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'subject', 'apartment', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at', 'apartment')
    search_fields = ('sender__username', 'receiver__username', 'subject', 'content')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'notification_type', 'title', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('user__username', 'title', 'message')
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)
