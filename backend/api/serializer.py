from rest_framework import serializers
from .model.dailytip import DailyTip
from .model.healthtip import HealthTip

class HealthTipSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthTip
        fields = ["id", "source", "external_id", "title", "body", "published_at"]

class DailyTipSerializer(serializers.ModelSerializer):
    tip = HealthTipSerializer()

    class Meta:
        model = DailyTip
        fields = ["date", "tip"]
