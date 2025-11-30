from django.urls import path
from . import views

app_name = 'tickets'

urlpatterns = [
    path('', views.home, name='home'),
    path('tickets/', views.ticket_list, name='ticket_list'),
    path('tickets/<int:pk>/', views.ticket_detail, name='ticket_detail'),
    path('about/', views.about, name='about'),
]
