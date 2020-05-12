from django.urls import path
from . import views


urlpatterns = [
    path('', views.ListingByCategoryListView.as_view(), name='listing-by-category'),
    path(
        '<str:category>/<slug:slug>/',
        views.ListingDetailView.as_view(), name='listing-detail'
    ),
]
