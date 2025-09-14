from backend.basemodel import TimeBaseModel
from .healthtip import HealthTip
from django.db import models


class DailyTip(TimeBaseModel):
    tip = models.ForeignKey("HealthTip", on_delete=models.CASCADE)
    date = models.DateField() 

    def __str__(self):
        return f"{self.date}: {self.tip}"
