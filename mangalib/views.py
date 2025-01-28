from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.core.validators import validate_email
from .models import User
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from .models import Claim,ClaimType,ClaimResponsable
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login as auth_login
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth import update_session_auth_hash
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import update_session_auth_hash
from .forms import UserUpdateForm, PasswordChangeForm
from django.contrib import messages as django_messages  # Pour afficher des messages de succès ou d'erreur
from .models import Message
from .forms import MessageForm








def page_accueil(request):
    return render(request,'page_accueil.html')

def login_client(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.role == 'citoyen': 
                user.last_login = timezone.now()
                user.save() # Vérifiez que l'utilisateur a le rôle 'citoyen'
                login(request, user)
                return redirect('page_index')  # Remplacez 'home' par le nom de la vue où vous voulez rediriger après la connexion réussie
            else:
                messages.error(request, "You are not authorized to access this platform.")
        else:
            messages.error(request, 'Invalid username or password')

    return render(request, 'authentification/auth_Client/sign_in_Client.html')


def register_client(request):
    error = False
    message = ""
    
    if request.method == "POST":
        username = request.POST.get('username', None)
        name = request.POST.get('name', None)
        email = request.POST.get('email', None)
        password = request.POST.get('password', None)
        repassword = request.POST.get('repassword', None)
        
        # Validation de l'email
        try:
            validate_email(email)
        except ValidationError:
            error = True
            message = "Please enter a valid email address"
        
        # Vérification des mots de passe
        if error == False:
            if password != repassword:
                error = True
                message = "Les deux mots de passe ne sont pas identiques"
        
        # Vérification de l'unicité de l'email
        if error == False:
            if User.objects.filter(email=email).exists():
                error = True
                message = "Un utilisateur avec cet email existe déjà"
        
        # Création de l'utilisateur
        if error == False:
            hashed_password = make_password(password)  # Hasher le mot de passe
            User.objects.create(
                username=username,
                name=name,
                email=email,
                password=hashed_password,
                role='citoyen',
                
            )
            message = "Inscription réussie"
            return redirect('login_client')  # Rediriger vers la page de login après l'inscription réussie
    
    context = {
        'error': error,
        'message': message
    }
    
    return render(request, 'authentification/auth_Client/sign_up_Client.html', context)
def login_Employee(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.role == 'agent':
                return redirect('page_accueil_agent')
            elif user.role=='responsable_traitement':
                return redirect('recieve_claim')
            elif user.role == 'fonctionnaire':
                return redirect('search_claims_date')
            elif user.role=='manager':
                return redirect('Dashboard')
            elif user.role == 'admin':
                if user.is_staff and user.is_superuser:
                    return redirect(reverse('admin:index'))
                else:
                    messages.error(request, 'You do not have permission to access the admin interface.')
          
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'authentification/auth_User/connexion_emp.html')
def page_index(request):
    return render(request, 'Citizen/index.html')


def submit_claim(request):
    if request.method == 'POST':
        citizen_name = request.POST.get('name')
        citizen_email = request.POST.get('email')
        citizen_contact = request.POST.get('phone')
        citizen_address = request.POST.get('address')
        ID_card= request.POST.get('CIN')
        claim_type_id = request.POST.get('claim_type')  # ID du ClaimType
        claim_description = request.POST.get('description')

        status = 'non_traitée'
        created_by = 'Citizen'

        # Récupérer l'objet ClaimType correspondant
        try:
            claim_type = ClaimType.objects.get(id=claim_type_id)
        except ClaimType.DoesNotExist:
            messages.error(request, "Type de réclamation invalide.")
            return redirect('submit_claim')  # Redirige vers la même page pour réessayer

        # Création et sauvegarde de la réclamation
        new_claim = Claim(
            citizen_name=citizen_name,
            citizen_email=citizen_email,
            citizen_contact=citizen_contact,
            citizen_adresse=citizen_address,
            CIN=ID_card,
            claim_type=claim_type,  # Assignation correcte de l'objet ClaimType
            claim_description=claim_description,
            status=status,
            created_by=created_by
        )
        new_claim.save()

        messages.success(request, 'Votre réclamation a été soumise avec succès !')
        return redirect('page_sms')  # Redirection vers une page de confirmation ou d'accueil

    # Récupérer tous les types de réclamation depuis la base de données
    claim_types = ClaimType.objects.all()
    return render(request, 'Citizen/Soumettre.html', {'claim_types': claim_types})

def page_sms(request):
    return render(request, 'Citizen/sms.html')

def page_suivre_claim(request):
    return render(request, 'Citizen/Suivre.html')

#Agent de sécurité

def page_accueil_agent(request):
    return render(request,'security_agent/page_accueil.html' )



def add_claim(request):
    if request.method == 'POST':
        citizen_name = request.POST.get('citizen_name')
        citizen_email = request.POST.get('citizen_email')
        citizen_contact = request.POST.get('citizen_contact')
        citizen_address = request.POST.get('citizen_adresse')
        id_card = request.POST.get('CIN')
        claim_type_name = request.POST.get('claim_type')
        claim_description = request.POST.get('description')

        status = 'non_traitée'

        # Récupérer l'instance ClaimType correspondante
        try:
            claim_type = ClaimType.objects.get(name=claim_type_name)
        except ClaimType.DoesNotExist:
            messages.error(request, "Le type de réclamation sélectionné n'existe pas.")
            return redirect('add_claim')  # Redirection vers le formulaire en cas d'erreur

        # Création et sauvegarde de la réclamation
        new_claim = Claim(
            citizen_name=citizen_name,
            citizen_email=citizen_email,
            citizen_contact=citizen_contact,
            citizen_adresse=citizen_address,
            CIN=id_card,
            claim_type=claim_type,
            claim_description=claim_description,
            status=status,
            created_by='Agent'
        )
        new_claim.save()
        
        messages.success(request, 'La réclamation a été soumise avec succès !')
        return redirect('add_claim')  # Redirection vers une page de confirmation ou d'accueil

    # Récupérer les types de réclamations depuis la base de données
    claim_types = ClaimType.objects.all()
    return render(request, 'security_agent/add_claim.html', {'claim_types': claim_types})

def edit_delete_claim(request):
    agent_claims = Claim.objects.filter(created_by='Agent')
    claim_types = ClaimType.objects.all()
    messages.success(request, 'La réclamation a été changée avec succès !')
    return render(request, 'security_agent/edit_delete.html', {'claims': agent_claims, 'claim_types': claim_types})

#la vue du suppression de la reclamation
@csrf_exempt
def delete_claim(request, claim_id):
    if request.method == "POST":
        claim = get_object_or_404(Claim, id=claim_id)
        claim.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=400)
# la vue du mise à jour des données
def update_claim(request, claim_id):
    if request.method == "POST":
        claim = get_object_or_404(Claim, id=claim_id)
        claim.citizen_name = request.POST.get('citizen_name')
        claim.citizen_email = request.POST.get('citizen_email')
        claim.citizen_contact = request.POST.get('citizen_contact')
        claim.citizen_adresse = request.POST.get('citizen_adresse')
        claim.CIN = request.POST.get('CIN')
        claim.claim_type_id = request.POST.get('claim_type')   # Mise à jour du type de réclamation
        claim.claim_description = request.POST.get('claim_description')
        claim.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=400)

#les vues du plateforme du fonctionnaire 

def search_claims_date(request):
    if request.method == 'GET':
        search_date = request.GET.get('date', None)
        message = None
        if search_date:
            # Filtrer les réclamations par date
            claims = Claim.objects.filter(date_of_claim__date=search_date)
            if not claims:
                message = f"Aucune réclamation trouvée pour la date {search_date}."
        else:
            # Si aucune date n'est spécifiée, afficher toutes les réclamations
            claims = Claim.objects.all()

        # Charger tous les messages pour la boîte de réception
        messages = Message.objects.all().order_by('date_sent')

        context = {
            'claims': claims,
            'message': message,  # Ajouter un message pour informer l'utilisateur
            'messages': messages  # Ajouter les messages pour le template
        }

        return render(request, 'official/page_accueil_fonc.html', context)

    
#une vue pour la mise à jour du statut
def update_claim_status(request):
    if request.method == 'POST':
        claim_id = request.POST.get('claim_id')
        new_status = request.POST.get('status')

        try:
            claim = Claim.objects.get(id=claim_id)
            claim.status = new_status
            claim.save()
            return JsonResponse({'success': True})
        except Claim.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Claim not found'})
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


#Manager

def Dashboard(request):
    # Récupérer les 10 réclamations les plus récentes
    claims = Claim.objects.order_by('-date_of_claim')[:10]



   
    
    # Compter les réclamations selon le statut et assignation
    not_assigned_claims_count = Claim.objects.filter(is_assigned=False).count()
    not_treated_claims_count = Claim.objects.filter(status='non_traitée',is_assigned=True).count()
    
    
    # Créer un contexte avec les réclamations et les comptages
    context = {
        'claims': claims, 
        'not_assigned_claims_count': not_assigned_claims_count,
        'not_treated_claims_count': not_treated_claims_count,
    }
    
    return render(request, 'manager/dashboard.html', context)


def validate_claim_dashboard(request, claim_id):
    claim = get_object_or_404(Claim, id=claim_id)
    if request.method == 'POST':
        claim.validation_status = 'validée'
        claim.save()
        messages.success(request, f"La réclamation {claim.numero_claim} a été validée.")
    return redirect('Dashboard')

# View for rejecting a claim
def reject_claim_dashboard(request, claim_id):
    claim = get_object_or_404(Claim, id=claim_id)
    if request.method == 'POST':
        claim.validation_status = 'rejetée'
        claim.save()
        messages.success(request, f"La réclamation {claim.numero_claim} a été rejetée.")
    return redirect('Dashboard')




def Affectation(request):
    employees = User.objects.filter(role='responsable_traitement')  # Récupérer les employés ayant ce rôle
    error_message = None

    if request.method == 'POST':
        claim_number = request.POST.get('claim_number')
        employee_id = request.POST.get('employee')

        # Vérifier si la réclamation existe
        claim = Claim.objects.filter(numero_claim=claim_number).first()

        if not claim:
            error_message = "Numéro de réclamation non trouvé."
        else:
            employee = get_object_or_404(User, id=employee_id)

            # Créer une nouvelle entrée dans ClaimResponsable
            ClaimResponsable.objects.create(claim=claim, responsable=employee)
            messages.success(request, f"La réclamation {claim.numero_claim} a été affectée avec succès à {employee.name}.")

            # Rediriger vers la même page après succès
            return redirect('Affectation')  

    return render(request, 'manager/affectation.html', {'employees': employees, 'error_message': error_message})




#une vue pour recupérer les réclamations par date (la vue de l'interface claim

def claims_date(request):
    if request.method == 'GET':
        search_date = request.GET.get('date-search', None)
        message = None
        if search_date:
            claims = Claim.objects.filter(date_of_claim__date=search_date) 
            if not claims:
               message = f"Aucune réclamation trouvée pour la date {search_date}."
        else:
            claims = Claim.objects.all() 

 
        context = {
            'claims': claims,
            'message': message,
            'search_date': search_date  # Ajouter la date recherchée au contexte
        }
        return render(request, 'manager/claims.html', context)
#une vue pour valider 
def validate_claim(request, claim_id):
    claim = get_object_or_404(Claim, id=claim_id)
    claim.validation_status = "Validée"
    claim.save()
    messages.success(request, "La réclamation a été validée.")
    return redirect('claims_date')

#une  vue pour rejeter
def reject_claim(request, claim_id):
    claim = get_object_or_404(Claim, id=claim_id)
    claim.validation_status = "Rejetée"
    claim.save()
    messages.error(request, "La réclamation a été rejetée.")
    return redirect('claims_date')
    
@login_required
def profile(request):
 
    user = request.user  # Récupère l'utilisateur connecté

    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=user)
        password_form = PasswordChangeForm(user, request.POST)

        if user_form.is_valid():
            user_form.save()
            messages.success(request, 'Votre profil a été mis à jour avec succès.')
            return redirect('account_settings_agent')

        if password_form.is_valid():
            user = password_form.save()
            update_session_auth_hash(request, user)  # Important pour ne pas déconnecter l'utilisateur après le changement de mot de passe
            messages.success(request, 'Votre mot de passe a été mis à jour avec succès.')
            return redirect('account_settings_agent')
    else:
        user_form = UserUpdateForm(instance=user)
        password_form = PasswordChangeForm(user)

    context = {
        'user_form': user_form,
        'password_form': password_form
    }
    return render(request,'manager/profile.html',context)
    


# une vue pour la mise à jour de is assigned
def update_claim_is_assigned(request, claim_id):
    claim = get_object_or_404(Claim, id=claim_id)
    if request.method == 'POST':
        claim.is_assigned = not claim.is_assigned
        claim.save()
        return redirect('Dashboard')
    
# déconnexion
def logout_client(request):
    logout(request)
    return redirect('login_client')


def logout_employee(request):
    logout(request)
    return redirect('login_Employee')


def update_is_assigned_claim(request, claim_id):
    claim = get_object_or_404(Claim, id=claim_id)
    if request.method == 'POST':
        claim.is_assigned = not claim.is_assigned
        claim.save()
        return redirect('claims_date')


@login_required
def account_settings_agent(request):
 
    user = request.user  # Récupère l'utilisateur connecté

    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=user)
        password_form = PasswordChangeForm(user, request.POST)

        if user_form.is_valid():
            user_form.save()
            messages.success(request, 'Votre profil a été mis à jour avec succès.')
            return redirect('account_settings_agent')

        if password_form.is_valid():
            user = password_form.save()
            update_session_auth_hash(request, user)  # Important pour ne pas déconnecter l'utilisateur après le changement de mot de passe
            messages.success(request, 'Votre mot de passe a été mis à jour avec succès.')
            return redirect('account_settings_agent')
    else:
        user_form = UserUpdateForm(instance=user)
        password_form = PasswordChangeForm(user)

    context = {
        'user_form': user_form,
        'password_form': password_form
    }
    return render(request,'security_agent/profile.html',context)


@login_required
def account_settings_fonc(request):
 
    user = request.user  # Récupère l'utilisateur connecté

    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=user)
        password_form = PasswordChangeForm(user, request.POST)

        if user_form.is_valid():
            user_form.save()
            messages.success(request, 'Votre profil a été mis à jour avec succès.')
            return redirect('account_settings_fonc')

        if password_form.is_valid():
            user = password_form.save()
            update_session_auth_hash(request, user)  # Important pour ne pas déconnecter l'utilisateur après le changement de mot de passe
            messages.success(request, 'Votre mot de passe a été mis à jour avec succès.')
            return redirect('account_settings_fonc')
    else:
        user_form = UserUpdateForm(instance=user)
        password_form = PasswordChangeForm(user)

    context = {
        'user_form': user_form,
        'password_form': password_form
    }
    return render(request,'official/profile.html',context)

@login_required
def Responsable_traitement(request):
    # Récupérer l'utilisateur connecté (le responsable)
    responsable = request.user

    # Récupérer les réclamations affectées au responsable
    assigned_claims = Claim.objects.filter(
        claimresponsable__responsable=responsable
    ).select_related('claim_type')  # Optimisation avec select_related

    # Gestion de l'envoi de message
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = responsable  # Le responsable connecté est l'expéditeur du message
            message.save()
            django_messages.success(request, 'Message envoyé avec succès.')
            return redirect('recieve_claim')  # Redirige après l'envoi pour vider le formulaire
    else:
        form = MessageForm()  # Formulaire vide pour l'envoi de message

    # Contexte pour le template
    context = {
        'assigned_claims': assigned_claims,  # Les réclamations du responsable
        'form': form,  # Le formulaire d'envoi de message
    }
    
    return render(request, 'Responsable/receive_claim.html', context)

     


     
 


