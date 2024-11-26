from django.urls import path
from .views import tfidf_search, home

urlpatterns = [
    path('search/', tfidf_search, name='tfidf_search'),
    path('home/',home,name='home')
]
