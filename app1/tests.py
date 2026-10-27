from django.test import TestCase
from django.test import override_settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes


@override_settings(PASSWORD_HASHERS=['django.contrib.auth.hashers.MD5PasswordHasher'])
class AuthenticationTests(TestCase):
    def setUp(self):
        self.username = 'nala'
        self.password = 'PecesSeguros_123'
        get_user_model().objects.create_user(
            username=self.username,
            password=self.password,
        )

    def test_anonymous_visitors_see_welcome_instead_of_game_template(self):
        response = self.client.get(reverse('hola'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "¡Bienvenidos a Nala's Fish Quest!")
        self.assertContains(response, 'Iniciar sesión y entrar')
        self.assertContains(response, 'Crear una cuenta')
        self.assertNotContains(response, '🎮 Mecánicas del Juego')

    def test_login_page_matches_site_and_shows_navbar(self):
        response = self.client.get(reverse('login'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Iniciar sesión')
        self.assertContains(response, 'La historia')
        self.assertContains(response, 'csrfmiddlewaretoken')

    def test_valid_credentials_start_session_and_return_home(self):
        response = self.client.post(
            reverse('login'),
            {'username': self.username, 'password': self.password},
        )

        self.assertRedirects(response, reverse('hola'))
        self.assertTrue(response.wsgi_request.user.is_authenticated)
        home = self.client.get(reverse('hola'))
        self.assertContains(home, f'¡Hola, {self.username}!')
        self.assertContains(home, 'Cerrar sesión')
        self.assertContains(home, '🎮 Mecánicas del Juego')

    def test_invalid_credentials_show_error(self):
        response = self.client.post(
            reverse('login'),
            {'username': self.username, 'password': 'incorrecta'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'no son correctos')
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_logout_ends_session_and_returns_home(self):
        self.client.force_login(get_user_model().objects.get(username=self.username))

        response = self.client.post(reverse('logout'))

        self.assertRedirects(response, reverse('hola'))
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        home = self.client.get(reverse('hola'))
        self.assertContains(home, 'Iniciar sesión')


@override_settings(
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
    PASSWORD_HASHERS=['django.contrib.auth.hashers.MD5PasswordHasher'],
)
class RegistrationAndRecoveryTests(TestCase):
    def setUp(self):
        self.user_model = get_user_model()
        self.user = self.user_model.objects.create_user(
            username='nala',
            email='nala@example.com',
            password='Vela-azul_68!Tormenta',
        )

    def test_registration_creates_account_and_starts_session(self):
        response = self.client.post(
            reverse('registro'),
            {
                'username': 'pescador',
                'email': '  PESCADOR@example.com ',
                'password1': 'MarAbierto_2026!Pez',
                'password2': 'MarAbierto_2026!Pez',
            },
        )

        self.assertRedirects(response, reverse('hola'))
        new_user = self.user_model.objects.get(username='pescador')
        self.assertEqual(new_user.email, 'pescador@example.com')
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_registration_rejects_duplicate_email(self):
        response = self.client.post(
            reverse('registro'),
            {
                'username': 'otro',
                'email': 'NALA@example.com',
                'password1': 'MarAbierto_2026!Pez',
                'password2': 'MarAbierto_2026!Pez',
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Ya existe una cuenta con este correo')
        self.assertFalse(self.user_model.objects.filter(username='otro').exists())

    def test_password_reset_sends_email_for_registered_address(self):
        response = self.client.post(
            reverse('password_reset'),
            {'email': self.user.email},
        )

        self.assertRedirects(response, reverse('password_reset_done'))
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('restablecer/', mail.outbox[0].body)
        self.assertIn(self.user.username, mail.outbox[0].body)

    def test_password_reset_response_does_not_disclose_unknown_email(self):
        response = self.client.post(
            reverse('password_reset'),
            {'email': 'desconocido@example.com'},
        )

        self.assertRedirects(response, reverse('password_reset_done'))
        self.assertEqual(len(mail.outbox), 0)

    def test_valid_reset_link_changes_password(self):
        uid = urlsafe_base64_encode(force_bytes(self.user.pk))
        token = default_token_generator.make_token(self.user)
        response = self.client.get(
            reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token}),
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        response = self.client.post(
            response.request['PATH_INFO'],
            {
                'new_password1': 'Nuevo-Mar_2026!Pez',
                'new_password2': 'Nuevo-Mar_2026!Pez',
            },
        )

        self.assertRedirects(response, reverse('password_reset_complete'))
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('Nuevo-Mar_2026!Pez'))
