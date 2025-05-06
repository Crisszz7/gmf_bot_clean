from django.contrib import admin
from .models import MessageTemplate, PlaceTrigal, WhatsappUser

# Register your models here.
admin.site.register(MessageTemplate),
admin.site.register(PlaceTrigal),
admin.site.register(WhatsappUser),