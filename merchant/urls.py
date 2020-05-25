from django.urls import path
from . import views


urlpatterns = [
    path('', views.SquareManagementView.as_view(), name='square-manage'),
    path(
        'callback/', views.SquareCallbackView.as_view(), name='square-callback'
    ),
    path('revoke/', views.SquareRevokeView.as_view(), name='square-revoke'),
    path('renew/', views.SquareRenewView.as_view(), name='square-renew'),
]
