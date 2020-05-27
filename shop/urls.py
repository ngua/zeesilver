from django.urls import path
from . import views


app_name = 'shop'


urlpatterns = [
    path('order/', views.OrderCreateView.as_view(), name='order'),
    path('review/', views.ReviewOrderView.as_view(), name='review'),
    path('update/', views.UpdateOrderView.as_view(), name='update'),
    path('pay/', views.PaymentView.as_view(), name='pay'),
    path('cancel/', views.CancelOrderView.as_view(), name='cancel'),
]
