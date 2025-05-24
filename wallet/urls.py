from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path
from . import views

urlpatterns = [
    path('', LoginView.as_view(template_name='wallet/login.html'), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),

    path('register/', views.register_view, name='register'),
    path('verify_email/', views.verify_email_view, name='verify_email'),
    path('dashboard/', views.dashboard_view, name='wallet_dashboard'),

    path('add-funds/', views.add_funds_view, name='add_funds'),
    path('withdraw/', views.withdraw_funds_view, name='withdraw_funds'),
    path('transfer/', views.transfer_funds_view, name='transfer_funds'),
]