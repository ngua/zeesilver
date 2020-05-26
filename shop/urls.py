from django.urls import path
from . import views


app_name = 'shop'


urlpatterns = [
    path('order/', views.OrderCreateView.as_view(), name='order'),
    path('pay/', views.OrderCreateView.as_view(), name='pay'),
]
