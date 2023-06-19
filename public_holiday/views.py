from rest_framework import viewsets

from .models import PublicHoliday
from .serializers import PublicholidaySerializer


class PublicHolidayList(viewsets.ReadOnlyModelViewSet):
    """
    A simple list and model detail ViewSet.
    """

    queryset = PublicHoliday.objects.all().order_by("id")
    serializer_class = PublicholidaySerializer
