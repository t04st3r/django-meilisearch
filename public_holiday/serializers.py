from rest_framework import serializers
from .models import PublicHoliday


class PublicholidaySerializer(serializers.ModelSerializer):
    class Meta:
        model = PublicHoliday
        fields = "__all__"
