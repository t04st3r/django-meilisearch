import datetime
import random
import requests

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django_countries import countries
from public_holiday.models import PublicHoliday


class Command(BaseCommand):
    help = (
        "Populate PublicHoliday models from Public Holiday API"
        + "(see https://date.nager.at/Api) given a random country"
    )
    api_consumed = False

    def handle(self, *args, **options):
        while not self.api_consumed:
            (country_code, country_name) = random.choice(list(countries))
            current_date = datetime.date.today()
            url = "%s/publicholidays/%s/%s" % (
                settings.PUBLIC_HOLDAY_API_URL,
                current_date.year,
                country_code,
            )
            try:
                response = requests.get(url)
                response.raise_for_status()
                # CloudFlare sometimes respond with a no content,
                # we will keep requesting data
                if response.status_code == 200:
                    data = response.json()
                    self.api_consumed = True
            except Exception as error:
                raise CommandError(
                    "Error while fetching Public Holiday API [%s]" % str(error)
                )
        holydays = [
            PublicHoliday(
                date=hd["date"],
                name=hd["name"],
                local_name=hd["localName"],
                country=hd["countryCode"],
            )
            for hd in data
        ]
        PublicHoliday.objects.bulk_create(
            holydays,
            ignore_conflicts=True,
        )

        self.stdout.write(
            self.style.SUCCESS(
                "Successfully populate data for country %s, %i record processed"
                % (country_name, len(data))
            )
        )
