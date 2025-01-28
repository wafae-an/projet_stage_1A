from django.contrib import admin
from .models import User 
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
 # Assurez-vous que le modèle User est correctement importé

# Définissez la classe d'administration pour le modèle User


class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('username','name', 'email', 'role', 'is_active', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_active')
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Permissions', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser')}),
        ('Important dates', {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username','name', 'email', 'password1', 'password2', 'role', 'is_active', 'is_staff', 'is_superuser')}
        ),
    )
    search_fields = ('email', 'username')
    ordering = ('email',)


admin.site.register(User, CustomUserAdmin)

# Si tu veux changer le logo directement dans l'interface admin
class MyAdminSite(admin.AdminSite):
    site_header = 'Ma plateforme'
    site_title = 'Administration'
    index_title = 'Bienvenue'
    # Inclure le logo si nécessaire
    site_url = '/media/logo/logo.png'  # Assure-toi que le chemin est correct
admin_site = MyAdminSite(name='myadmin')



