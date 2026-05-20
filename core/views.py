from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import User, Apartment, Reservation, Message, Notification
from .forms import UserRegistrationForm, ApartmentForm, ReservationForm, MessageForm


def home(request):
    """Page d'accueil avec liste des appartements"""
    apartments = Apartment.objects.filter(is_active=True, is_validated=True)
    
    # Filtres de recherche
    city = request.GET.get('city')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    check_in = request.GET.get('check_in')
    check_out = request.GET.get('check_out')
    
    if city:
        apartments = apartments.filter(Q(city__icontains=city) | Q(address__icontains=city))
    
    if min_price:
        apartments = apartments.filter(price_per_night__gte=min_price)
    
    if max_price:
        apartments = apartments.filter(price_per_night__lte=max_price)
    
    context = {
        'apartments': apartments,
        'search_params': request.GET.dict(),
    }
    return render(request, 'core/home.html', context)


def register(request):
    """Inscription d'un nouvel utilisateur"""
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password1'])
            user.save()
            messages.success(request, 'Votre compte a été créé avec succès. Vous pouvez maintenant vous connecter.')
            return redirect('login')
    else:
        form = UserRegistrationForm()
    
    return render(request, 'core/register.html', {'form': form})


def user_login(request):
    """Connexion d'un utilisateur"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Bienvenue {user.username} !')
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
        else:
            messages.error(request, 'Nom d\'utilisateur ou mot de passe incorrect.')
    
    return render(request, 'core/login.html')


@login_required
def user_logout(request):
    """Déconnexion d'un utilisateur"""
    logout(request)
    messages.info(request, 'Vous avez été déconnecté.')
    return redirect('home')


@login_required
def profile(request):
    """Gestion du profil utilisateur"""
    if request.method == 'POST':
        request.user.first_name = request.POST.get('first_name', '')
        request.user.last_name = request.POST.get('last_name', '')
        request.user.email = request.POST.get('email', '')
        request.user.phone = request.POST.get('phone', '')
        if request.FILES.get('avatar'):
            request.user.avatar = request.FILES.get('avatar')
        request.user.save()
        messages.success(request, 'Votre profil a été mis à jour avec succès.')
        return redirect('profile')
    
    return render(request, 'core/profile.html')


@login_required
def apartment_list(request):
    """Liste des appartements (pour le propriétaire et l'administrateur)"""
    if request.user.role == 'proprietaire':
        apartments = Apartment.objects.filter(owner=request.user)
    elif request.user.role == 'admin':
        apartments = Apartment.objects.all()
    else:
        apartments = Apartment.objects.filter(is_active=True, is_validated=True)
    
    return render(request, 'core/apartment_list.html', {'apartments': apartments})


@login_required
def apartment_detail(request, pk):
    """Détail d'un appartement"""
    apartment = get_object_or_404(Apartment, pk=pk)
    return render(request, 'core/apartment_detail.html', {'apartment': apartment})


@login_required
def apartment_create(request):
    """Création d'un nouvel appartement (propriétaire uniquement)"""
    if request.user.role != 'proprietaire':
        messages.error(request, 'Seuls les propriétaires peuvent créer des appartements.')
        return redirect('home')
    
    if request.method == 'POST':
        form = ApartmentForm(request.POST, request.FILES)
        if form.is_valid():
            apartment = form.save(commit=False)
            apartment.owner = request.user
            apartment.save()
            messages.success(request, 'Votre appartement a été créé avec succès et est en attente de validation.')
            
            # Créer une notification pour l'administrateur
            admins = User.objects.filter(role='admin')
            for admin in admins:
                Notification.objects.create(
                    user=admin,
                    notification_type='validation',
                    title='Nouvel appartement à valider',
                    message=f'{request.user.username} a soumis un nouvel appartement: {apartment.title}',
                    link=f'/admin/core/apartment/{apartment.id}/change/'
                )
            
            return redirect('apartment_list')
    else:
        form = ApartmentForm()
    
    return render(request, 'core/apartment_form.html', {'form': form, 'action': 'create'})


@login_required
def apartment_update(request, pk):
    """Modification d'un appartement"""
    apartment = get_object_or_404(Apartment, pk=pk)
    
    if request.user.role == 'proprietaire' and apartment.owner != request.user:
        messages.error(request, 'Vous ne pouvez modifier que vos propres appartements.')
        return redirect('apartment_list')
    
    if request.method == 'POST':
        form = ApartmentForm(request.POST, request.FILES, instance=apartment)
        if form.is_valid():
            form.save()
            messages.success(request, 'L\'appartement a été modifié avec succès.')
            return redirect('apartment_detail', pk=apartment.pk)
    else:
        form = ApartmentForm(instance=apartment)
    
    return render(request, 'core/apartment_form.html', {'form': form, 'action': 'update', 'apartment': apartment})


@login_required
def apartment_delete(request, pk):
    """Suppression d'un appartement"""
    apartment = get_object_or_404(Apartment, pk=pk)
    
    if request.user.role == 'proprietaire' and apartment.owner != request.user:
        messages.error(request, 'Vous ne pouvez supprimer que vos propres appartements.')
        return redirect('apartment_list')
    
    if request.method == 'POST':
        apartment.delete()
        messages.success(request, 'L\'appartement a été supprimé avec succès.')
        return redirect('apartment_list')
    
    return render(request, 'core/apartment_confirm_delete.html', {'apartment': apartment})


@login_required
def reservation_create(request, apartment_pk):
    """Création d'une réservation"""
    apartment = get_object_or_404(Apartment, pk=apartment_pk)
    
    if request.user.role != 'client':
        messages.error(request, 'Seuls les clients peuvent effectuer des réservations.')
        return redirect('home')
    
    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.apartment = apartment
            reservation.client = request.user
            reservation.total_amount = reservation.calculate_total()
            reservation.save()
            messages.success(request, 'Votre réservation a été créée avec succès.')
            
            # Créer une notification pour le propriétaire
            Notification.objects.create(
                user=apartment.owner,
                notification_type='reservation',
                title='Nouvelle réservation',
                message=f'{request.user.username} a réservé votre appartement {apartment.title}',
                link=f'/reservations/{reservation.id}/'
            )
            
            return redirect('reservation_history')
    else:
        form = ReservationForm()
    
    return render(request, 'core/reservation_form.html', {'form': form, 'apartment': apartment})


@login_required
def reservation_history(request):
    """Historique des réservations de l'utilisateur"""
    if request.user.role == 'client':
        reservations = Reservation.objects.filter(client=request.user)
    elif request.user.role == 'proprietaire':
        reservations = Reservation.objects.filter(apartment__owner=request.user)
    elif request.user.role == 'admin':
        reservations = Reservation.objects.all()
    else:
        reservations = Reservation.objects.none()
    
    return render(request, 'core/reservation_history.html', {'reservations': reservations})


@login_required
def reservation_detail(request, pk):
    """Détail d'une réservation"""
    reservation = get_object_or_404(Reservation, pk=pk)
    
    # Vérifier les permissions
    if request.user.role == 'client' and reservation.client != request.user:
        messages.error(request, 'Vous ne pouvez voir que vos propres réservations.')
        return redirect('reservation_history')
    
    if request.user.role == 'proprietaire' and reservation.apartment.owner != request.user:
        messages.error(request, 'Vous ne pouvez voir que les réservations de vos appartements.')
        return redirect('reservation_history')
    
    return render(request, 'core/reservation_detail.html', {'reservation': reservation})


@login_required
def reservation_cancel(request, pk):
    """Annulation d'une réservation"""
    reservation = get_object_or_404(Reservation, pk=pk)
    
    # Vérifier les permissions
    if request.user.role == 'client' and reservation.client != request.user:
        messages.error(request, 'Vous ne pouvez annuler que vos propres réservations.')
        return redirect('reservation_history')
    
    if request.method == 'POST':
        reservation.status = 'cancelled'
        reservation.save()
        messages.success(request, 'La réservation a été annulée avec succès.')
        return redirect('reservation_history')
    
    return render(request, 'core/reservation_confirm_cancel.html', {'reservation': reservation})


@login_required
def message_list(request):
    """Liste des messages de l'utilisateur"""
    sent_messages = Message.objects.filter(sender=request.user)
    received_messages = Message.objects.filter(receiver=request.user)
    
    return render(request, 'core/message_list.html', {
        'sent_messages': sent_messages,
        'received_messages': received_messages,
    })


@login_required
def message_create(request, receiver_id=None):
    """Création d'un nouveau message"""
    if receiver_id:
        receiver = get_object_or_404(User, pk=receiver_id)
    else:
        receiver = None
    
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = request.user
            if receiver:
                message.receiver = receiver
            message.save()
            
            # Créer une notification
            Notification.objects.create(
                user=message.receiver,
                notification_type='message',
                title='Nouveau message',
                message=f'Vous avez reçu un nouveau message de {request.user.username}',
                link=f'/messages/{message.id}/'
            )
            
            messages.success(request, 'Votre message a été envoyé avec succès.')
            return redirect('message_list')
    else:
        form = MessageForm()
    
    return render(request, 'core/message_form.html', {'form': form, 'receiver': receiver})


@login_required
def notification_list(request):
    """Liste des notifications de l'utilisateur"""
    notifications = Notification.objects.filter(user=request.user)
    
    # Marquer toutes les notifications comme lues
    notifications.update(is_read=True)
    
    return render(request, 'core/notification_list.html', {'notifications': notifications})

# --- ESPACE ADMINISTRATEUR ---

@login_required
def admin_dashboard(request):
    """Tableau de bord pour l'administrateur"""
    if request.user.role != 'admin':
        messages.error(request, "Accès refusé. Vous n'avez pas les droits d'administrateur.")
        return redirect('home')
    
    context = {
        'total_users': User.objects.count(),
        'total_apartments': Apartment.objects.count(),
        'total_reservations': Reservation.objects.count(),
        'pending_apartments': Apartment.objects.filter(is_validated=False),
        'recent_reservations': Reservation.objects.all()[:5],
    }
    return render(request, 'core/admin_dashboard.html', context)

@login_required
def admin_apartment_validate(request, pk):
    """Action de validation d'un appartement par l'administrateur"""
    if request.user.role != 'admin':
        messages.error(request, "Accès refusé.")
        return redirect('home')
    
    apartment = get_object_or_404(Apartment, pk=pk)
    apartment.is_validated = True
    apartment.is_active = True
    apartment.save()
    
    # Notifier le propriétaire
    Notification.objects.create(
        user=apartment.owner,
        notification_type='validation',
        title='Appartement validé !',
        message=f'Votre appartement "{apartment.title}" a été validé par l\'administrateur et est maintenant en ligne.',
        link=f'/apartments/{apartment.id}/'
    )
    
    messages.success(request, f'L\'appartement "{apartment.title}" a été validé avec succès.')
    return redirect('admin_dashboard')
