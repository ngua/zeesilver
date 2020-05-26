from django.urls import path
from . import views


app_name = 'listing'


urlpatterns = [
    path('', views.ListingFilterView.as_view(), name='filter'),
    path(
        '<str:category>/<slug:slug>/',
        views.ListingDetailView.as_view(),
        name='detail'
    ),
]
