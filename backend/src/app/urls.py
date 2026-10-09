from django.contrib import admin
from django.urls import path
from api.api import api
from django.urls import include


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", api.urls),  # include the API URLs
]
