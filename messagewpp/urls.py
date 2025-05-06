from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('home/', views.home, name="home"),
    path('whatsapp/', views.Whatsapp, name='whatsapp' ),
    path('requestUser/', views.requestUser, name="requestUser" ),
    path('webhook/', views.handleWhatsapp, name="webhook"),
    path('webhookfb/', views.webhook, name='webhookfb'),
    path('descargar-excel/<int:sede_id>/', views.descargar_excel, name="descargar-excel"),
    path("requestUser/<int:postulacion_id>/", views.edit_postulacion_function , name="postulacion-edit"),
    path('whatsapp/<int:message_template_user_id>', views.delete_message_template_user_funcion, name="message-delete")
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

