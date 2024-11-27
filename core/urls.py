from django.urls import path
from .views import home, group_search_view, particular_search_view

urlpatterns = [
    path("api/group_search/", group_search_view, name="group_search"),
    path("api/particular_search/", particular_search_view, name="particular_search"),
    path("home/", home, name="home"),
]
