from django.db import models

# Create your models here.
class SurveyResponse(models.Model):
    reason_for_learning = models.CharField(max_length=100)
    english_level = models.CharField(max_length=100)