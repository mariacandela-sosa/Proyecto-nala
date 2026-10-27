from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy
from . import views

urlpatterns = [
    path('', views.inicio, name='hola'),
    path('registro/', views.registro, name='registro'),
    path(
        'login/',
        auth_views.LoginView.as_view(
            template_name='app1/login.html',
            next_page='hola',
        ),
        name='login',
    ),
    path(
        'logout/',
        auth_views.LogoutView.as_view(next_page='hola'),
        name='logout',
    ),
    path(
        'recuperar-cuenta/',
        auth_views.PasswordResetView.as_view(
            template_name='app1/password_reset_form.html',
            email_template_name='app1/password_reset_email.html',
            subject_template_name='app1/password_reset_subject.txt',
            success_url=reverse_lazy('password_reset_done'),
        ),
        name='password_reset',
    ),
    path(
        'recuperar-cuenta/enviado/',
        auth_views.PasswordResetDoneView.as_view(
            template_name='app1/password_reset_done.html',
        ),
        name='password_reset_done',
    ),
    path(
        'restablecer/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='app1/password_reset_confirm.html',
            success_url=reverse_lazy('password_reset_complete'),
        ),
        name='password_reset_confirm',
    ),
    path(
        'restablecer/completo/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name='app1/password_reset_complete.html',
        ),
        name='password_reset_complete',
    ),
]