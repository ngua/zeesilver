from django.urls import path
from . import views


app_name = 'merchant'


urlpatterns = [
    path('', views.SquareManagementView.as_view(), name='manage'),
    path('callback/', views.SquareCallbackView.as_view(), name='callback'),
    path('revoke/', views.SquareRevokeView.as_view(), name='revoke'),
    path('renew/', views.SquareRenewView.as_view(), name='renew'),
]
