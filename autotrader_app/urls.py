
from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from autotrader_app import views

urlpatterns = [
    path('/', views.CarList.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
