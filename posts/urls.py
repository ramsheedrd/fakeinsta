from django.urls import path
from . import views

urlpatterns = [
    path("", views.home_view, name="home"),
    path("add/", views.add_post, name="add_post"),
    path('delete/<int:post_id>/', views.delete_post, name="delete_post"),
    path('like/<post_id>/', views.like_toggle),
    path('comment/add/', views.add_comment),
    ]
