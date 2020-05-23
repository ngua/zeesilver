from django.urls import path
from . import views


urlpatterns = [
    path(
        'authorize/', views.SquareAuthView.as_view(), name='square-authorize'
    ),
    path(
        'callback/', views.SquareCallbackView.as_view(), name='square-callback'
    ),
    path('revoke/', views.SquareRevokeView.as_view(), name='square-revoke'),
]
