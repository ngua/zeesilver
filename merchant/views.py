import logging
from django.conf import settings
from django.contrib import messages
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.utils.http import urlencode
from django.views.generic import TemplateView, View
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.mixins import PermissionRequiredMixin
from square.client import Client
from .models import SquareConfig
from .utils import square_connect_request


logger = logging.getLogger(__name__)


@method_decorator(staff_member_required, name='dispatch')
class SquareViewMixin(PermissionRequiredMixin, View):
    """
    Mixin to ensure proper permissions and auth status before accessing
    Square OAuth views. Initializes Square OAuth client for use in subsquent
    views
    Inherits from View as well as PermissionRequiredMixin in order to decorate
    dispatch method
    """
    permission_required = 'merchant.obtain_tokens'
    redirect_url = reverse_lazy('merchant:manage')

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

    def log_error(self, request_type, result):
        """
        Generic logging for failed requests to Square Connect
        """
        logger.error(
            (
                f'Square OAuth {request_type} failed: {result.errors} '
                f'({result.type})'
            )
        )


class SquareManagementView(SquareViewMixin, TemplateView):
    """
    Combined template view to manage existing Square tokens or initialize
    Square OAuth flow
    """
    template_name = 'merchant/management.html'
    http_method_names = ['get']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Construct the query parameters and url to make the request to Square
        # endpoint
        if not self.square_config.active:
            params = urlencode({
                'client_id': settings.SQUARE_APPLICATION_ID,
                'scope': 'PAYMENTS_WRITE PAYMENTS_READ'
            })
            context['url'] = (
                f'https://{settings.SQUARE_DOMAIN}/'
                f'{settings.SQUARE_AUTH_URL}?{params}'
            )
        context['config_active'] = self.square_config.active
        return context


class SquareCallbackView(SquareViewMixin):
    """
    Callback that makes request to Square OAuth endpoint. Upon success,
    tokens are committed to database as binary after being encrypted with
    Fernet
    """
    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        # Authorization code returned from Square
        auth_code = request.GET.get('code')

        if not auth_code:
            messages.error(self.request, 'Square Connect authorization failed')
            logger.error('Failed to connect to Square OAuth endpoint')
            return redirect(self.redirect_url)

        body = square_connect_request(
            grant_type='authorization_code', code=auth_code
        )
        result = self.oauth_api.obtain_token(body)

        if result.is_success():
            # Update the square_config singleton instance
            self.square_config.update(body=result.body, user=self.request.user)
            logger.info('Square OAuth authorization succeeded')
            messages.success(self.request, 'Authorization successful')
        # Check `is_error` explicitly
        elif result.is_error():
            self.log_error('authorization', result)
            messages.error(self.request, 'Authorization failed')

        return redirect(self.redirect_url)


class SquarePostableMixin(SquareViewMixin):
    def setup(self, request, *args, **kwargs):
        """
        Ensure that OAuth tokens exist before continuing
        """
        super().setup(request, *args, **kwargs)
        if not self.square_config.active:
            # Redirect to manage view if no tokens currently exist,
            # alerting user
            messages.info(
                (
                    'No active Square configuration currently exists, please '
                    'authorize application'
                )
            )
            return redirect(self.redirect_url)


class SquareRevokeView(SquarePostableMixin):
    """
    Revokes existing OAuth tokens associated with SquareConfig object.
    """
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        """
        Constructs and makes request to Square OAuth revocation endpoint.
        Upon success, calls `reset` method of SquareConfig to delete its
        current instance and erase the tokens stored in db
        """
        authorization = f'Client {settings.SQUARE_APPLICATION_SECRET}'
        # Manually construct the body, since its parameters differ from the
        # other two requests (i.e. includes access token, but excludes client
        # secret)
        body = {
            'client_id': settings.SQUARE_APPLICATION_ID,
            'access_token': self.square_config.access_token
        }
        result = self.oauth_api.revoke_token(body, authorization)

        if result.is_success():
            logger.info('Square OAuth successfully revoked')
            messages.info(self.request, 'Authorization revoked')
            # Delete the existing SquareConfig instance
            self.square_config.reset()
        # Again, check `is_error` explicitly
        elif result.is_error():
            self.log_error('revocation', result)
            messages.error(self.request, 'Revocation failed')

        return redirect(self.redirect_url)


class SquareRenewView(SquarePostableMixin):
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        body = square_connect_request(
            grant_type='refresh_token',
            refresh_token=self.square_config.refresh_token
        )
        result = self.oauth_api.obtain_token(body)
        if result.is_success():
            logger.info('Square OAuth renewal succeeded')
            messages.success(self.request, 'Authorization renewed')
            # Update the existing SquareConfig instance
            self.square_config.update(body=result.body, user=self.request.user)
        elif result.is_error():
            self.log_error('renewal', result)
            messages.error(self.request, 'Renewal failed')

        return redirect(self.redirect_url)
