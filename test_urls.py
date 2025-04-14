"""
Custom URL patterns for testing
"""
from django.urls import path
from django.urls import include

urlpatterns = [
    path('', include('workbench.urls')),
]

