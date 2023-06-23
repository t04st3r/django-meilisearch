import meilisearch
from django.conf import settings
from django.core.management.base import BaseCommand
from meilisearch.errors import MeilisearchApiError, MeilisearchCommunicationError
from public_holiday.models import PublicHoliday
from public_holiday.serializers import PublicholidaySerializer


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
                documents = PublicholidaySerializer(public_holidays, many=True)
                # Add the documents to the index
                index.add_documents(documents.data)
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
