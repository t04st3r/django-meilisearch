from unittest.mock import MagicMock, patch

from meilisearch.errors import MeilisearchApiError
import pytest
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from .factories import PublicHolidayFactory, MockResponse
from public_holiday.serializers import PublicholidaySerializer


@pytest.mark.django_db
class TestPublicHolidayAPI:
    meilisearch_response = [
        {
            "date": "2023-02-20",
            "local_name": "Carnevale",
            "name": "Carnival",
            "country": "IT",
            "id": "2",
        },
        {
            "date": "2023-12-25",
            "local_name": "Natale",
            "name": "Christmas",
            "country": "IT",
            "id": "1",
        },
    ]

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

    @patch("public_holiday.views.meilisearch.Client")
    def test_search_action(self, MockMeiliSearchClient):
        # Mock the MeiliSearch client
        client_instance = MagicMock()
        client_instance.index.return_value = client_instance
        client_instance.update_sortable_attributes.return_value = client_instance
        client_instance.search.return_value = {"hits": self.meilisearch_response}
        MockMeiliSearchClient.return_value = client_instance

        # Create an instance of the API client
        api_client = APIClient()

        # Make a GET request to the search endpoint
        response = api_client.get(
            "/public_holiday/search/",
            {"q": "query", "sort": "country", "fields": ["country", "name"]},
        )

        # Assert the response status code
        assert response.status_code == 200

        # Assert the response data
        expected_data = self.meilisearch_response
        assert response.data == expected_data

        # Assert the MeiliSearch client calls
        client_instance.index.assert_called_with("public_holiday")
        client_instance.update_sortable_attributes.assert_called_with(
            list(PublicholidaySerializer().fields)
        )
        # Assert proper args are passed to the search method
        args, _ = client_instance.search.call_args
        assert args[0] == "query"
        assert type(args[1]) == dict
        assert args[1]["sort"] == ["country:asc"]

        # Under the hood a set is used to check duplicates
        # hence the elements order is not preserved anymore
        # however we will assert that correct attributes are passed along
        attributes_to_retrieve = args[1]["attributesToRetrieve"]
        assert len(attributes_to_retrieve) == 2
        assert "country" in attributes_to_retrieve
        assert "name" in attributes_to_retrieve

    @patch("public_holiday.views.meilisearch.Client")
    def test_search_action_duplicate_fields(self, MockMeiliSearchClient):
        # Mock the MeiliSearch client
        client_instance = MagicMock()
        client_instance.index.return_value = client_instance
        client_instance.update_sortable_attributes.return_value = client_instance
        client_instance.search.return_value = {"hits": self.meilisearch_response}
        MockMeiliSearchClient.return_value = client_instance

        # Create an instance of the API client
        api_client = APIClient()

        # Make a GET request to the search endpoint
        response = api_client.get(
            "/public_holiday/search/",
            {
                "q": "query",
                "sort": "country",
                "fields": ["country", "name", "country", "name"],
            },
        )

        # Assert the response status code
        assert response.status_code == 200

        # Assert the response data
        expected_data = self.meilisearch_response
        assert response.data == expected_data

        # Assert the MeiliSearch client calls
        client_instance.index.assert_called_with("public_holiday")
        client_instance.update_sortable_attributes.assert_called_with(
            list(PublicholidaySerializer().fields)
        )
        # Assert proper args are passed to the search method
        args, _ = client_instance.search.call_args
        assert args[0] == "query"
        assert type(args[1]) == dict
        assert args[1]["sort"] == ["country:asc"]

        # Under the hood a set is used to check duplicates
        # hence the elements order is not preserved anymore
        # however we will assert that duplicate fields are removed
        attributes_to_retrieve = args[1]["attributesToRetrieve"]
        assert len(attributes_to_retrieve) == 2
        assert "country" in attributes_to_retrieve
        assert "name" in attributes_to_retrieve

    @patch("public_holiday.views.meilisearch.Client")
    def test_search_action_sort_desc(self, MockMeiliSearchClient):
        # Mock the MeiliSearch client
        client_instance = MagicMock()
        client_instance.index.return_value = client_instance
        client_instance.update_sortable_attributes.return_value = client_instance
        client_instance.search.return_value = {"hits": self.meilisearch_response}
        MockMeiliSearchClient.return_value = client_instance

        # Create an instance of the API client
        api_client = APIClient()

        # Make a GET request to the search endpoint note the dash
        # in the sort param value
        response = api_client.get(
            "/public_holiday/search/",
            {"q": "query", "sort": "-country"},
        )

        # Assert the response status code
        assert response.status_code == 200

        # Assert the response data
        expected_data = self.meilisearch_response
        assert response.data == expected_data

        # Assert the MeiliSearch client calls
        client_instance.index.assert_called_with("public_holiday")
        client_instance.update_sortable_attributes.assert_called_with(
            list(PublicholidaySerializer().fields)
        )
        # Assert proper args are passed to the search method
        args, _ = client_instance.search.call_args
        assert args[0] == "query"
        assert type(args[1]) == dict
        assert args[1]["sort"] == ["country:desc"]

    @patch("public_holiday.views.meilisearch.Client")
    def test_search_action_default_sort_with_invalid_sort_param(
        self, MockMeiliSearchClient
    ):
        # Mock the MeiliSearch client
        client_instance = MagicMock()
        client_instance.index.return_value = client_instance
        client_instance.update_sortable_attributes.return_value = client_instance
        client_instance.search.return_value = {"hits": self.meilisearch_response}
        MockMeiliSearchClient.return_value = client_instance

        # Create an instance of the API client
        api_client = APIClient()

        # Make a GET request to the search endpoint note the dash
        # in the sort param value
        response = api_client.get(
            "/public_holiday/search/",
            {"q": "query", "sort": "-pizza"},
        )

        # Assert the response status code
        assert response.status_code == 200

        # Assert the response data
        expected_data = self.meilisearch_response
        assert response.data == expected_data

        # Assert the MeiliSearch client calls
        client_instance.index.assert_called_with("public_holiday")
        client_instance.update_sortable_attributes.assert_called_with(
            list(PublicholidaySerializer().fields)
        )
        # Assert proper args are passed to the search method
        args, _ = client_instance.search.call_args
        assert args[0] == "query"
        assert type(args[1]) == dict
        assert args[1]["sort"] == ["id:asc"]

    @patch("public_holiday.views.meilisearch.Client")
    def test_search_action_with_invalid_fields(self, MockMeiliSearchClient):
        # Mock the MeiliSearch client
        client_instance = MagicMock()
        client_instance.index.return_value = client_instance
        client_instance.update_sortable_attributes.return_value = client_instance
        client_instance.search.return_value = {"hits": self.meilisearch_response}
        MockMeiliSearchClient.return_value = client_instance

        # Create an instance of the API client
        api_client = APIClient()

        # Make a GET request to the search endpoint with invalid fields
        response = api_client.get(
            "/public_holiday/search/", {"fields": "invalid_field"}
        )

        # Assert the response status code
        assert response.status_code == 200

        # Assert that all fields are included in the response data
        expected_data = self.meilisearch_response
        assert response.data == expected_data

        # Assert the MeiliSearch client calls
        client_instance.index.assert_called_with("public_holiday")
        client_instance.update_sortable_attributes.assert_called_with(
            list(PublicholidaySerializer().fields)
        )
        client_instance.search.assert_called_with(
            "",
            {
                "sort": ["id:asc"],
                "attributesToRetrieve": ["*"],
            },
        )

    @patch("public_holiday.views.meilisearch.Client")
    def test_search_action_with_error(self, MockMeiliSearchClient):
        # Mock the MeiliSearch client to raise an error
        client_instance = MagicMock()
        client_instance.index.return_value = client_instance
        client_instance.update_sortable_attributes.return_value = client_instance
        mock_response = MockResponse("", 500, error="Server Error")
        client_instance.search.side_effect = MeilisearchApiError(
            "An error occurred.", mock_response
        )
        MockMeiliSearchClient.return_value = client_instance

        # Create an instance of the API client
        api_client = APIClient()

        # Make a GET request to the search endpoint
        response = api_client.get(
            "/public_holiday/search/", {"q": "query", "sort": "id"}
        )

        # Assert the response status code
        assert response.status_code == 500

        # Assert the response data
        expected_data = {"detail": "Error while fetching data from meilisarch"}
        assert response.data == expected_data

        # Assert the MeiliSearch client calls
        client_instance.index.assert_called_with("public_holiday")
        client_instance.update_sortable_attributes.assert_called_with(
            list(PublicholidaySerializer().fields)
        )
        client_instance.search.assert_called_with(
            "query",
            {
                "sort": ["id:asc"],
                "attributesToRetrieve": ["*"],
            },
        )
