"""
Custom URL patterns for testing
"""
from django.urls import include, re_path

urlpatterns = [
    re_path(r'^', include('workbench.urls')),
]

