from django.urls import path
from . import views

urlpatterns = [
    path('', views.getFiles.as_view(), name='GetFiles'),
    path('create/', views.CreateFiles.as_view(), name='CreateFiles'),
]