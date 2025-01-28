from django.urls import path
from . import views
from django.contrib import admin

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accueil/', views. page_accueil, name='page_accueil'),
    path('sign-in-client/', views.login_client, name='login_client'),
    path('sign-up-client/', views.register_client, name='register_client'),    
    path('sign-in-employee/', views.login_Employee, name='login_Employee'),
    #plateforme du citoyen
    path('page-index/', views.page_index, name='page_index'),
    path('submit-claim/', views. submit_claim, name='submit_claim'),
    path('page-sms/', views. page_sms, name='page_sms'),
    path('page-suivre-claim/', views. page_suivre_claim, name='page-suivre-claim'),
    #plateforme de l'agent de sécurité
    path('page-accueil-agent/', views.page_accueil_agent , name='page_accueil_agent'),
    path('page-add-claim/', views.add_claim , name='add_claim'),
    path('edit-delete-claim/', views.edit_delete_claim, name='edit_delete_claim'),
    path('delete-claim/<int:claim_id>/', views.delete_claim, name='delete_claim'),
    path('update-claim/<int:claim_id>/', views.update_claim, name='update_claim'),
    path('profile_agent/', views.account_settings_agent, name='profile_agent'),
    #plateforme du fonctionnaire
    path('page-accueil-fonc/', views.search_claims_date, name='search_claims_date'),
    path('update-status/', views.update_claim_status, name='update_claim_status'),
    path('profile_fonc/', views.account_settings_fonc, name='profile_fonc'),
    #plateforme du manager
    path('dashboard/', views.Dashboard, name='Dashboard'),
    path('claims_manager/', views.claims_date, name='claims_date'),
    path('affectation/', views.Affectation, name='Affectation'),
    path('account_settings/', views.profile, name='profile'),
    path('update_claim/<int:claim_id>/', views.update_claim_is_assigned, name='update_claim_is_assigned'),
    path('update_is_assigned/<int:claim_id>/', views.update_is_assigned_claim, name='update_is_assigned_claim'),
    path('validate-claim/<int:claim_id>/', views.validate_claim, name='validate_claim'),
    path('reject-claim/<int:claim_id>/', views.reject_claim, name='reject_claim'),
     path('validate_claim_dashboard/<int:claim_id>/', views.validate_claim_dashboard, name='validate_claim_dashboard'),
    path('reject_claim_dashboard/<int:claim_id>/', views.reject_claim_dashboard, name='reject_claim_dashboard'),
    #plateforme du responsable de traitement 
    path('recieve_claim/', views.Responsable_traitement, name='recieve_claim'),
    #Déconnexion
    path('logoutc/', views.logout_client, name='logoutc'),
    path('logoute/', views.logout_employee, name='logoute'),


]

    
