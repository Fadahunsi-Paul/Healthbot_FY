from django.core.management.base import BaseCommand
from api.utils.utils import fetch_daily_health_tip

class Command(BaseCommand):
    help = "Fetches today's health tip from MyHealthfinder → CDC → AdviceSlip"

    def handle(self, *args, **kwargs):
        tip = fetch_daily_health_tip()
        if tip:
            self.stdout.write(self.style.SUCCESS(f"Today's tip saved: {tip}"))
        else:
            self.stdout.write(self.style.ERROR("Failed to fetch any tip"))
