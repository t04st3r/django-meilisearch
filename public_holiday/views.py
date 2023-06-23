import meilisearch
from django.conf import settings
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from meilisearch.errors import MeilisearchApiError
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import APIException

from .models import PublicHoliday
from .serializers import PublicholidaySerializer


class PublicHolidayList(viewsets.ReadOnlyModelViewSet):
    """
    A simple list and model detail ViewSet.
    """

    queryset = PublicHoliday.objects.all().order_by("id")
    serializer_class = PublicholidaySerializer

    # Custom action to query meilisearch

    @extend_schema(
        parameters=[
            OpenApiParameter("q", OpenApiTypes.STR, OpenApiParameter.QUERY),
            OpenApiParameter("sort", OpenApiTypes.STR, OpenApiParameter.QUERY),
            OpenApiParameter("fields", OpenApiTypes.OBJECT, OpenApiParameter.QUERY),
        ]
    )
    @action(
        methods=["GET"],
        detail=False,
    )
    def search(self, request):
        try:
            # Configure MeiliSearch client
            client = meilisearch.Client(
                settings.MEILISEARCH_URL, settings.MEILISEARCH_API_KEY
            )
            model_fields = list(PublicholidaySerializer().fields)
            # Configure index
            client.index("public_holiday").update_sortable_attributes(
                model_fields,
            )
            # Get fields parameter, cast to set to get unique elements
            fields = set(request.query_params.getlist("fields", []))

            # Validate fields parameter, if not valid all the fields would be included
            attribute_to_restrieve = (
                list(fields)
                if fields.issubset(set(model_fields)) and len(fields) > 0
                else ["*"]
            )

            # Get query filter parameter
            query = request.query_params.get("q", "")

            # Get sort parameter
            sort_field = request.query_params.get("sort", "id")
            sort_order = "asc"
            # Handle descending order if sort param is prefixed by a dash
            if sort_field.startswith("-"):
                sort_field = sort_field[1:]
                sort_order = "desc"

            # Validate sort parameter,
            # if validation fails fallback sort value to default
            if sort_field not in model_fields:
                sort_field = "id"
                sort_order = "asc"

            # Fetch documents from MeiliSearch index
            response = client.index("public_holiday").search(
                query,
                {
                    "sort": [f"{sort_field}:{sort_order}"],
                    "attributesToRetrieve": attribute_to_restrieve,
                },
            )
            documents = response["hits"]
        except MeilisearchApiError:
            raise APIException("Error while fetching data from meilisarch")
        return Response(documents)
