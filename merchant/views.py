import logging
from django.conf import settings
from django.contrib import messages
from django.urls import reverse
from django.shortcuts import redirect
from django.utils.http import urlencode
from django.views.generic import TemplateView, View
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from square.client import Client
from .models import SquareConfig


logger = logging.getLogger(__name__)


@method_decorator(staff_member_required, name='dispatch')
class SquareViewMixin(PermissionRequiredMixin, View):
    """
    Mixin to ensure proper permissions and auth status before accessing
    Square OAuth views. Initializes Square OAuth client for use in subsquent
    views
    """
    permission_required = 'merchant.obtain_tokens'

    def setup(self, request, *args, **kwargs):
        super().setup(request, *args, **kwargs)
        # Initialize the Square OAuth client and SquareConfig singleton
        # instance, which is either retrieved or created
        client = Client(
            access_token=settings.SQUARE_ACCESS_TOKEN,
            environment=settings.SQUARE_ENVIRONMENT
        )
        self.oauth_api = client.o_auth
        self.square_config = SquareConfig.get_solo()


class SquareAuthView(SquareViewMixin, TemplateView):
    """
    View that initializes Square OAuth flow
    """
    template_name = 'merchant/authorize.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Construct the query parameters and url to make the request to Square
        params = urlencode({
            'client_id': settings.SQUARE_APPLICATION_ID,
            'scope': 'PAYMENTS_WRITE PAYMENTS_READ'
        })
        context['url'] = (
            f'https://{settings.SQUARE_DOMAIN}/'
            f'{settings.SQUARE_AUTH_URL}?{params}'
        )
        return context


class SquareCallbackView(SquareViewMixin):
    """
    Callback that makes request to Square OAuth endpoint. Upon success,
    tokens are committed to database in binary format after being encrypted
    with Fernet
    """
    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        # Authorization code returned from Square
        auth_code = request.GET.get('code')

        if not auth_code:
            messages.error(self.request, 'Square Connect authorization failed')
            logger.error('Failed to connect to Square auth endpoint')
            return redirect(reverse('index'))

        result = self.obtain_token(auth_code)
        if result.is_success():
            self.handle_success(result.body)
        else:
            self.handle_error()

        return redirect(reverse('index'))

    def obtain_token(self, auth_code):
        """
        Exchanges the authorization code for OAuth access token
        """
        body = {
            'client_id': settings.SQUARE_APPLICATION_ID,
            'client_secret': settings.SQUARE_APPLICATION_SECRET,
            'grant_type': 'authorization_code',
            'code': auth_code
        }
        return self.oauth_api.obtain_token(body)

    def handle_success(self, data):
        """
        Updates the singleton SquareConfig instance. `access_token`
        and `refresh_token` are encrypted before being committed to db
        """
        self.square_config.update(
            access_token=data.get('access_token', ''),
            refresh_token=data.get('refresh_token', ''),
            expires=data.get('expires_date', ''),
            user=self.request.user
        )
        logger.info('Square OAuth authorization succeeded')
        messages.success(self.request, 'Square authorization succeeded')

    def handle_error(self):
        logger.info('Square OAuth authorization failed')
        messages.error(self.request, 'Square authorization failed')


class SquareRevokeView(SquareViewMixin, TemplateView):
    """
    View to revoke existing OAuth tokens associated with SquareConfig object.
    Accepts both GET and POST requests
    """
    template_name = 'merchant/revoke.html'
    http_method_names = ['get', 'post']

    def post(self, request, *args, **kwargs):
        """
        Constructs and makes request to Square OAuth revocation endpoint.
        Upon success, calls `reset` method of SquareConfig to delete its
        current instance and erase tokens stored in db
        """
        authorization = f'Client {settings.SQUARE_APPLICATION_SECRET}'
        body = {
            'client_id': settings.SQUARE_APPLICATION_ID,
            'access_token': self.square_config.access_token
        }
        result = self.oauth_api.revoke_token(body, authorization)
        if result.is_success():
            logger.info('Square OAuth successfully revoked')
            messages.success(self.request, 'Square authorization revoked')
            # Delete the existing SquareConfig instance
            self.square_config.reset()
        else:
            logger.error('Square OAuth revocation failed')
            messages.error(self.request, 'Square revocation failed')

        return redirect(reverse('index'))
