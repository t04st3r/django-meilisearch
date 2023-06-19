import pytest

from django.utils import timezone

from public_holiday.tests.factories import PublicHolidayFactory


@pytest.mark.django_db
class TestPublicHoliday:
    def test_public_holiday_str(self):
        today = timezone.now().date()
        model = PublicHolidayFactory(
            name="Holy Moly", local_name="Santo Cielo!", date=today
        )
        assert (
            str(model) == f"[{model.country.name} | {today}] Holy Moly (Santo Cielo!)"
        )
