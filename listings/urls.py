from django.urls import path
from . import views


urlpatterns = [
    path('', views.ListingFilterView.as_view(), name='listing-filter'),
    path(
        '<str:category>/<slug:slug>/',
        views.ListingDetailView.as_view(), name='listing-detail'
    ),
]
