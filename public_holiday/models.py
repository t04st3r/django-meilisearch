from django.db import models
from django_countries.fields import CountryField


class PublicHoliday(models.Model):
    name = models.CharField(max_length=255)
    local_name = models.CharField(max_length=255)
    country = CountryField()
    date = models.DateField()

    class Meta:
        unique_together = ("country", "date", "local_name")

    def __str__(self) -> str:
        return "[%s | %s] %s (%s)" % (
            self.country.name,
            str(self.date),
            self.name,
            self.local_name,
        )
