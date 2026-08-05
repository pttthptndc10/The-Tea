from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    # Auth Routes
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_step1_view, name='register'),
    path('register/otp/', views.register_step2_otp_view, name='register_otp'),
    path('forgot-password/', views.forgot_password_step1_view, name='forgot_password'),
    path('forgot-password/otp/', views.forgot_password_step2_otp_view, name='forgot_password_otp'),
    path('forgot-password/reset/', views.reset_password_step3_view, name='reset_password'),
    path('resend-otp-api/', views.resend_otp_api_view, name='resend_otp_api'),

    # Member Overview Route (All Users)
    path('members/overview/', views.members_overview_view, name='members_overview'),

    # Admin Management Routes
    path('members/', views.member_list_view, name='member_list'),
    path('members/invite/', views.invite_member_view, name='invite_member'),
    path('members/<uuid:user_id>/toggle-status/', views.toggle_user_status_view, name='toggle_user_status'),
    path('members/<uuid:user_id>/delete/', views.delete_user_view, name='delete_user'),
    path('members/<uuid:user_id>/change-role/', views.change_user_role_view, name='change_user_role'),
    path('members/<uuid:user_id>/transfer-admin/', views.transfer_admin_view, name='transfer_admin'),
    # Direct Messaging API Routes
    path('api/messages/<uuid:target_user_id>/', views.get_direct_messages_api_view, name='get_direct_messages_api'),
    path('api/messages/send/', views.send_direct_message_api_view, name='send_direct_message_api'),
]

