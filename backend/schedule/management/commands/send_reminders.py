from datetime import timedelta

from django.core.mail import send_mail
from django.core.management.base import BaseCommand
from django.utils import timezone

from schedule.models import ScheduleItem


class Command(BaseCommand):
    help = "Надіслати листи-нагадування про пункти розкладу, що починаються протягом 24 годин"

    def handle(self, *args, **options):
        now = timezone.now()
        items = ScheduleItem.objects.filter(
            trip__reminders_enabled=True,
            reminder_sent=False,
            start__gte=now,
            start__lte=now + timedelta(hours=24),
        ).select_related("trip")

        sent = 0
        for item in items:
            emails = list(
                item.trip.members.exclude(user__email="").values_list(
                    "user__email", flat=True
                )
            )
            if emails:
                send_mail(
                    subject=f"Нагадування: {item.title}",
                    message=(
                        f"Поїздка «{item.trip.title}»\n"
                        f"{item.title} о {timezone.localtime(item.start):%d.%m %H:%M}"
                        f"{', ' + item.location if item.location else ''}"
                    ),
                    from_email=None,
                    recipient_list=emails,
                )
                sent += 1
            item.reminder_sent = True
            item.save(update_fields=["reminder_sent"])

        self.stdout.write(f"Надіслано нагадувань: {sent}")