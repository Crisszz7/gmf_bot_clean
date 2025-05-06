import os
from django.db import models
import pandas as pd
from django.contrib.auth.models import AbstractUser

#Modelo para alamecnar las sedes
class PlaceTrigal(models.Model):
    namePlace = models.CharField(max_length=30) 

    def __str__(self):
        return self.namePlace
    
#Modelo para alamacenar los datos de un usuario de Whatsaap
class WhatsappUser(models.Model):
    phoneNumberUser = models.CharField(max_length=30, unique=True)
    nameUser = models.CharField(max_length=40, null=True)
    documentUser = models.CharField(max_length=20, unique=True, null=True)
    # ageUser = models.IntegerField()
    # bornDateUser = models.CharField(max_length=10)
    experienceUser = models.TextField(max_length=400, default='...')
    placeTrigal = models.ForeignKey(PlaceTrigal, on_delete=models.PROTECT, null=True, blank=True)
    placeUser = models.TextField(max_length=60, null=True)
    imageUser = models.ImageField(upload_to='user_files/', null=True, blank=True)
    cvUser = models.FileField(upload_to='user_files/', null=True, blank=True)
    estado = models.CharField(max_length=50, blank=True, null=True)
    dateRequestUser = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return ( 
        str(self.phoneNumberUser) + 
        str(self.nameUser) + 
        str(self.documentUser) + 
        # str(self.ageUser) +
        # str(self.bornDateUser) +
        str(self.placeTrigal) + 
        str(self.experienceUser) +
        str(self.placeUser) + 
        str(self.cvUser) +
        str(self.estado) +
        str(self.dateRequestUser)
    )

    # def __str__(self):
    # return f"Usuario: {self.nameUser} ({self.phoneNumberUser}), Documento: {self.documentUser}"


class UploadedFile(models.Model):
    title = models.CharField(max_length=50)
    file = models.FileField(upload_to='uploads/')
    place = models.ForeignKey(PlaceTrigal, on_delete=models.CASCADE, null=True, blank=True)

    def get_columns(self):
        try:
            df = pd.read_excel(self.file.path)
            return df.columns.tolist()
        except:
            return []

    def get_data(self):
        try:
            df = pd.read_excel(self.file.path)
            return df.to_dict(orient='records')
        except:
            return []
        
    def delete(self, *args, **kwargs):
        # Eliminar el archivo físico antes de borrar el registro
        if self.file:
            if os.path.isfile(self.file.path):
                os.remove(self.file.path)
        super().delete(*args, **kwargs)

    def __str__(self):
        return self.title + " "+ str(self.file)
    

#Modelo para las plantillas de mensjaes
class MessageTemplate(models.Model):
    title = models.CharField(max_length=30)
    body = models.CharField(max_length=900)
    place = models.ForeignKey(PlaceTrigal, on_delete=models.CASCADE, null=True, blank=True)
    
    def __str__(self):
        return self.title + self.body