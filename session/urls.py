from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_function, name='login'),
    path('sign_up/', views.sign_up_function, name="sign_up"),
    path('logout/', views.logout_function, name="logout"),
    path('message-ai/', views.messages_ai_function, name="message-ai"),
    path('message-ai/<int:message_ai_id>/', views.details_edit_message_ai_function, name="message-ai_details"),
    path('message-ai/<int:message_ai_id>/delete/', views.delete_message_ai_function , name="message-ai_delete"),
    path('sign_up/<int:admin_id>/delete/', views.delete_place_admin_function, name="sign_up-delete" )
]
