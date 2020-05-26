from django.urls import path
from . import views


app_name = 'cart'


urlpatterns = [
    path('', views.CartStatusView.as_view(), name='status'),
    path('add/', views.CartAddView.as_view(), name='add'),
    path('remove/', views.CartRemoveView.as_view(), name='remove'),
    path('clear/', views.CartClearView.as_view(), name='clear'),
]
