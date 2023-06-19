import factory
import json
import random

import requests

from django_countries import countries


def _get_random_country():
    (country_code, _) = random.choice(list(countries))
    return country_code


# This create anonymous objects with properties passed as arguments
def Object(**kwargs):
    return type("Object", (), kwargs)


class MockResponse:
    headers = {"Content-Type": "application/json"}

    def __init__(self, data, status_code, url=None, error="MockResponseError"):
        self.status_code = status_code
        self.data = data
        self.content = data.encode()
        self.url = url
        self.request = Object(url=url)
        self.error = error

    def json(self):
        return json.loads(self.data)

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(self.error)


class PublicHolidayFactory(factory.django.DjangoModelFactory):
    country = factory.LazyFunction(_get_random_country)
    name = factory.Faker("name")
    local_name = factory.Faker("name")
    date = factory.Faker("past_date")

    class Meta:
        model = "public_holiday.PublicHoliday"
