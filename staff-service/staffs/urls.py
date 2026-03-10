from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('<int:staff_id>/', views.get_staff, name='get_staff'),
    path('', views.list_staff, name='list_staff'),
]
