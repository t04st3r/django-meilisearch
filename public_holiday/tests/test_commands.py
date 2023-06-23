import pytest

from io import StringIO

from django.core.management import call_command
from django.conf import settings
from public_holiday.tests.factories import MockResponse
from public_holiday.models import PublicHoliday
from public_holiday.serializers import PublicholidaySerializer
from public_holiday.tests.factories import PublicHolidayFactory
from meilisearch.errors import MeilisearchApiError, MeilisearchCommunicationError
from unittest import mock


def _call_command(command="populate_models", get_err=False, *args, **kwargs):
    out = StringIO()
    err = StringIO()
    call_command(
        command,
        *args,
        stdout=out,
        stderr=err,
        **kwargs,
    )
    return err.getvalue() if get_err else out.getvalue()


@pytest.mark.django_db
class TestPopulateModelsCommand:
    @mock.patch("requests.get")
    @mock.patch("random.choice")
    def test_populate_commands_success(self, fake_choice, fake_get):
        data = open("public_holiday/tests/fixtures.json").read()
        fake_get.side_effect = [MockResponse(str(data), 200)]
        fake_choice.return_value = ("PA", "Panama")
        result = _call_command()
        assert (
            "Successfully populate data for country Panama, 13 record processed\n"
            == result
        )
        ph_set = PublicHoliday.objects.all()
        assert len(ph_set) == 13
        for ph in ph_set:
            assert ph.country == "PA"

    @mock.patch("requests.get")
    def test_populate_commands_exception(self, fake_get):
        fake_get.side_effect = Exception("Network Error")
        with pytest.raises(Exception) as e_info:
            _call_command()
        assert (
            str(e_info.value)
            == "Error while fetching Public Holiday API [Network Error]"
        )
        ph_set = PublicHoliday.objects.all()
        assert len(ph_set) == 0

    @mock.patch("requests.get")
    def test_populate_commands_server_errror(self, fake_get):
        fake_get.side_effect = [MockResponse("", 500, error="Server Error")]
        with pytest.raises(Exception) as e_info:
            _call_command()
        assert (
            str(e_info.value)
            == "Error while fetching Public Holiday API [Server Error]"
        )
        ph_set = PublicHoliday.objects.all()
        assert len(ph_set) == 0

    @mock.patch("requests.get")
    @mock.patch("random.choice")
    def test_populate_commands_empty_response(self, fake_choice, fake_get):
        data = open("public_holiday/tests/fixtures.json").read()
        fake_get.side_effect = [MockResponse("[]", 204), MockResponse(str(data), 200)]
        fake_choice.return_value = ("PA", "Panama")
        result = _call_command()
        assert (
            "Successfully populate data for country Panama, 13 record processed\n"
            == result
        )
        ph_set = PublicHoliday.objects.all()
        assert len(ph_set) == 13
        for ph in ph_set:
            assert ph.country == "PA"


@pytest.mark.django_db
class TestPopulateMeilisearchIndexCommand:
    @mock.patch(
        "public_holiday.management.commands.populate_meilisearch_index.meilisearch.Client"
    )
    def test_command_with_public_holidays(self, mock_client):
        # Mock the MeiliSearch client and index
        mock_index = mock_client.return_value.index.return_value
        mock_index_name = "public_holiday"

        # Create test data using factory
        public_holidays = PublicHolidayFactory.create_batch(2)
        documents = PublicholidaySerializer(public_holidays, many=True)
        # Call the command to get the output
        result = _call_command("populate_meilisearch_index")

        # Assertions
        mock_client.assert_called_once_with(
            settings.MEILISEARCH_URL, settings.MEILISEARCH_API_KEY
        )
        mock_client.return_value.index.assert_called_once_with(mock_index_name)
        mock_index.add_documents.assert_called_once_with(documents.data)
        assert (
            'Successfully populated "public_holiday" index with 2 documents.\n'
            == result
        )

    @mock.patch(
        "public_holiday.management.commands.populate_meilisearch_index.meilisearch.Client"
    )
    def test_command_without_public_holidays(self, mock_client):
        # Mock the MeiliSearch client and index
        mock_index = mock_client.return_value.index.return_value
        mock_index_name = "public_holiday"

        # Call the command to get the stout
        result = _call_command("populate_meilisearch_index")

        # Assertions
        mock_client.assert_called_once_with(
            settings.MEILISEARCH_URL, settings.MEILISEARCH_API_KEY
        )
        mock_client.return_value.index.assert_called_once_with(mock_index_name)
        assert not mock_index.add_documents.called
        assert "No models found in your database\n" == result

    @mock.patch(
        "public_holiday.management.commands.populate_meilisearch_index.meilisearch.Client"
    )
    def test_command_meilisearch_api_error(self, mock_client):
        # Mock the MeiliSearch client and index to raise MeilisearchApiError
        mock_index = mock_client.return_value.index.return_value
        mock_response = MockResponse("", 500, error="Server Error")
        mock_index.add_documents.side_effect = MeilisearchApiError(
            "API error", mock_response
        )

        # Create test data using factory
        PublicHolidayFactory.create_batch(2)

        # Call the command to get the stderr
        result = _call_command("populate_meilisearch_index", get_err=True)

        # Assertions
        mock_client.assert_called_once_with(
            settings.MEILISEARCH_URL, settings.MEILISEARCH_API_KEY
        )
        mock_client.return_value.index.assert_called_once_with("public_holiday")
        mock_index.add_documents.assert_called_once()
        assert (
            result
            == "Error connecting to MeiliSearch: MeilisearchApiError. API error\n"
        )

    @mock.patch(
        "public_holiday.management.commands.populate_meilisearch_index.meilisearch.Client"
    )
    def test_command_meilisearch_communication_error(self, mock_client):
        # Mock the MeiliSearch client to raise MeilisearchCommunicationError
        mock_client.side_effect = MeilisearchCommunicationError("Communication error")

        # Call the command to get the stderr
        result = _call_command("populate_meilisearch_index", get_err=True)

        # Assertions
        mock_client.assert_called_once_with(
            settings.MEILISEARCH_URL, settings.MEILISEARCH_API_KEY
        )
        assert not mock_client.return_value.index.called
        assert (
            result
            == "Error connecting to MeiliSearch: MeilisearchCommunicationError, "
            + "Communication error\n"
        )
