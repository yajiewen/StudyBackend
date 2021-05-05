from django.db import models

# Create your models here.
class Table(models.Model):
    usr_account = models.CharField(max_length=20,primary_key= True)
    usr_password = models.CharField(max_length=20)
    
