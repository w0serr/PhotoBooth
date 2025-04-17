from django.urls import path
from . import views
from django.contrib.auth.views import LoginView
from .views import custom_logout_view
from .views import HomeView

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('requests/', views.RequestListView.as_view(), name='request_list'),
    path('requests/<int:pk>/', views.RequestDetailView.as_view(), name='request_detail'),
    path('requests/create/', views.RequestCreateView.as_view(), name='request_create'),
    path('requests/change_status/<int:pk>/', views.change_status, name='change_status'),
    path('requests/delete/<int:pk>/', views.delete_request, name='delete_request'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('pricing/', HomeView.as_view(), name='pricing'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('process/', views.ProcessView.as_view(), name='process'),
    path('contacts/', views.ContactsView.as_view(), name='contacts'),
    path('login/', LoginView.as_view(template_name='photobooth/login.html'), name='login'),
    path('register/', views.register, name='register'),
    path('requests/', views.RequestListView.as_view(), name='request_list'),
    path('requests/<int:pk>/', views.RequestDetailView.as_view(), name='request_detail'),
    path('requests/create/', views.RequestCreateView.as_view(), name='request_create'),
    path('logout/', custom_logout_view, name='logout'),
]