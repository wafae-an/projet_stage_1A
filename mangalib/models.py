from django.db import models
import random
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.conf import settings

# Gestionnaire d'utilisateurs personnalisé
class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError('L\'adresse email doit être fournie')
        if not username:
            raise ValueError('Le nom d\'utilisateur doit être fourni')
        if not extra_fields.get('role'):
            raise ValueError('Le rôle doit être fourni')
        if not extra_fields.get('name'):
            raise ValueError('Le nom doit être fourni')
        
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Le superutilisateur doit avoir is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Le superutilisateur doit avoir is_superuser=True.')
        if not extra_fields.get('role'):
            raise ValueError('Le superutilisateur doit avoir un rôle.')
        if not extra_fields.get('name'):
            raise ValueError('Le superutilisateur doit avoir un nom.')

        return self.create_user(username, email, password, **extra_fields)

# Modèle utilisateur personnalisé
class User(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('admin', 'Administrateur'),
        ('agent', 'Agent de sécurité'),
        ('fonctionnaire', 'Fonctionnaire'),
        ('manager', 'Manager'),
        ('responsable_traitement', 'Responsable du traitement')
    ]
    name = models.CharField(max_length=50, unique=True)
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=100, unique=True)
    role = models.CharField(max_length=30, choices=ROLE_CHOICES)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = ['email', 'role', 'name']

    def __str__(self):
        return self.username

# Modèle pour les réclamations (Claim)
class Claim(models.Model):
    STATUS_CHOICES = [
        ('traitée', 'Traitée'),
        ('non_traitée', 'Non traitée'),
        ('en_cours', 'En cours de traitement'),
    ]

    VALIDATION_CHOICES = [
        ('validée', 'Validée'),
        ('rejetée', 'Rejetée'),
        ('en_attente', 'En attente de validation'),
    ]

    citizen_name = models.CharField(max_length=100)
    citizen_email = models.EmailField(max_length=100)
    citizen_contact = models.CharField(max_length=100)
    citizen_adresse = models.CharField(max_length=100)
    CIN=models.CharField(max_length=100)
    claim_type = models.ForeignKey('ClaimType', on_delete=models.CASCADE)
    claim_description = models.CharField(max_length=500)
    date_of_claim = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='non_traitée')
    numero_claim = models.CharField(max_length=4, unique=True, blank=True, null=True)
    created_by = models.CharField(max_length=100, default='Agent')
    is_assigned = models.BooleanField(default=False)
    validation_status = models.CharField(max_length=20, choices=VALIDATION_CHOICES, default='en_attente')

    def save(self, *args, **kwargs):
        if not self.numero_claim:
            self.numero_claim = self.generate_unique_claim_number()
        super().save(*args, **kwargs)

    def generate_unique_claim_number(self):
        while True:
            numero_claim = f"{random.randint(1000, 9999)}"
            if not Claim.objects.filter(numero_claim=numero_claim).exists():
                return numero_claim

    def __str__(self):
        return f"Réclamation {self.numero_claim} - {self.claim_type.name} de {self.citizen_name} ({self.status})"

# Modèle pour les types de réclamations (ClaimType)
class ClaimType(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

# Modèle pour l'assignation des réclamations à un responsable
class ClaimResponsable(models.Model):
    claim = models.ForeignKey('Claim', on_delete=models.CASCADE)
    responsable = models.ForeignKey('User', on_delete=models.CASCADE)  # Utilisez la table User pour les employés
#modèle pour l'envoie et la reception des messages

class Message(models.Model):
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        related_name='sent_messages', 
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'responsable_traitement'}  # Seuls les responsables de traitement peuvent envoyer des messages
    )
    body = models.TextField()
    date_sent = models.DateTimeField(auto_now_add=True)

 


