from django.urls import path
from . import views

urlpatterns = [
    path('', views.getBranches.as_view(), name='GetBranch'),
    path('create/', views.CreateBranch.as_view(), name='CreateBranch'),
]