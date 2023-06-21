# myapp/management/commands/populate_public_holiday_index.py

import meilisearch
from django.conf import settings
from django.core.management.base import BaseCommand
from meilisearch.errors import MeilisearchApiError, MeilisearchCommunicationError
from public_holiday.models import PublicHoliday


class Command(BaseCommand):
    help = 'Populates MeiliSearch "public_holiday" index with PublicHoliday models'

    def handle(self, *args, **options):
        try:
            # Connect to MeiliSearch
            client = meilisearch.Client(
                settings.MEILISEARCH_URL, settings.MEILISEARCH_API_KEY
            )

            # Create or get the "public_holiday" index
            index_name = "public_holiday"
            index = client.index(index_name)
            # Get all PublicHoliday models from the database
            public_holidays = PublicHoliday.objects.all()

            if len(public_holidays) > 0:
                # Populate the index with PublicHoliday models
                for public_holiday in public_holidays:
                    # Convert PublicHoliday model to MeiliSearch document format
                    document = {
                        "id": str(public_holiday.id),
                        "country": str(public_holiday.country),
                        "name": public_holiday.name,
                        "local_name": public_holiday.local_name,
                        "date": public_holiday.date.isoformat(),
                    }

                    # Add the document to the index
                    index.add_documents([document])
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Successfully populated "{index_name}" index'
                        + f" with {public_holidays.count()} documents."
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING("No models found in your database")
                )
        except (MeilisearchApiError, MeilisearchCommunicationError) as e:
            self.stderr.write(
                self.style.ERROR(f"Error connecting to MeiliSearch: {str(e)}")
            )
