from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class User(AbstractUser):
    """Modèle utilisateur personnalisé avec gestion des rôles"""
    ROLE_CHOICES = [
        ('admin', 'Administrateur'),
        ('proprietaire', 'Propriétaire'),
        ('client', 'Client'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='client')
    phone = models.CharField(max_length=20, blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    class Meta:
        verbose_name = 'Utilisateur'
        verbose_name_plural = 'Utilisateurs'


class Apartment(models.Model):
    """Modèle représentant un appartement à louer"""
    title = models.CharField(max_length=200, verbose_name="Titre")
    description = models.TextField(verbose_name="Description")
    address = models.CharField(max_length=300, verbose_name="Adresse")
    city = models.CharField(max_length=100, verbose_name="Ville")
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Prix par nuit")
    bedrooms = models.PositiveIntegerField(verbose_name="Nombre de chambres")
    max_guests = models.PositiveIntegerField(verbose_name="Capacité maximale")
    photos = models.ImageField(upload_to='apartments/', blank=True, null=True)
    is_active = models.BooleanField(default=False, verbose_name="Actif")
    is_validated = models.BooleanField(default=False, verbose_name="Validé par l'administrateur")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='apartments', limit_choices_to={'role': 'proprietaire'})
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Appartement'
        verbose_name_plural = 'Appartements'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.city}"


class Reservation(models.Model):
    """Modèle représentant une réservation d'appartement"""
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('confirmed', 'Confirmée'),
        ('cancelled', 'Annulée'),
        ('completed', 'Terminée'),
    ]
    
    apartment = models.ForeignKey(Apartment, on_delete=models.CASCADE, related_name='reservations')
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reservations', limit_choices_to={'role': 'client'})
    check_in_date = models.DateField(verbose_name="Date d'arrivée")
    check_out_date = models.DateField(verbose_name="Date de départ")
    number_of_guests = models.PositiveIntegerField(verbose_name="Nombre de personnes")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Montant total")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Réservation'
        verbose_name_plural = 'Réservations'
        ordering = ['-check_in_date']
    
    def __str__(self):
        return f"{self.apartment.title} - {self.client.username} ({self.check_in_date} au {self.check_out_date})"
    
    def calculate_total(self):
        """Calcule le montant total de la réservation"""
        if self.check_in_date and self.check_out_date:
            nights = (self.check_out_date - self.check_in_date).days
            if nights > 0:
                return nights * float(self.apartment.price_per_night)
        return 0
    
    def save(self, *args, **kwargs):
        if not self.total_amount:
            self.total_amount = self.calculate_total()
        super().save(*args, **kwargs)


class Message(models.Model):
    """Modèle pour la messagerie entre utilisateurs"""
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    apartment = models.ForeignKey(Apartment, on_delete=models.SET_NULL, null=True, blank=True, related_name='messages')
    subject = models.CharField(max_length=200, blank=True, null=True, verbose_name="Sujet")
    content = models.TextField(verbose_name="Contenu")
    is_read = models.BooleanField(default=False, verbose_name="Lu")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.sender.username} -> {self.receiver.username}: {self.subject or self.content[:50]}"


class Notification(models.Model):
    """Modèle pour les notifications"""
    TYPE_CHOICES = [
        ('reservation', 'Réservation'),
        ('message', 'Message'),
        ('validation', 'Validation'),
        ('general', 'Général'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='general')
    title = models.CharField(max_length=200, verbose_name="Titre")
    message = models.TextField(verbose_name="Message")
    is_read = models.BooleanField(default=False, verbose_name="Lu")
    created_at = models.DateTimeField(auto_now_add=True)
    link = models.URLField(blank=True, null=True, verbose_name="Lien associé")
    
    class Meta:
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"
