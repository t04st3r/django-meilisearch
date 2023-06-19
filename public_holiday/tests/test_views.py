import pytest

from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient
from .factories import PublicHolidayFactory


@pytest.mark.django_db
class TestPublicHolidayAPI:
    def test_public_holiday_list_success(self):
        batch = PublicHolidayFactory.create_batch(10)
        client = APIClient()
        response = client.get("/public_holiday/")
        assert response.status_code == status.HTTP_200_OK
        batch_ids = [model.id for model in batch]
        response_dict = response.json()
        assert response_dict["count"] == 10
        for model in response_dict["results"]:
            assert model["id"] in batch_ids

    def test_public_holiday_detail_success(self):
        today = timezone.now().date()
        model = PublicHolidayFactory(
            name="Holy Moly", local_name="Santo Cielo!", date=today
        )
        client = APIClient()
        response = client.get(f"/public_holiday/{model.id}/")
        assert response.status_code == status.HTTP_200_OK
        response_dict = response.json()
        assert response_dict["id"] == model.id
        assert response_dict["date"] == str(model.date)
        assert response_dict["name"] == model.name
        assert response_dict["local_name"] == model.local_name
        assert response_dict["country"] == str(model.country)
