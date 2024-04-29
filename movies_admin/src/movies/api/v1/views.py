from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import Q, Case, When, Value, CharField
from django.http import JsonResponse
from django.views.generic.list import BaseListView
from django.views.generic.detail import BaseDetailView

from movies.models import Filmwork, PersonFilmwork


class MoviesApiMixin:
    model = Filmwork
    http_method_names = ["get"]

    def get_queryset(self):
        return (
            Filmwork.objects.prefetch_related("genres", "persons")
            .values(
                "id",
                "title",
                "description",
                "creation_date",
                "rating",
            )
            .annotate(
                type=Case(
                    When(type="MV", then=Value("movie")),
                    When(type="TV", then=Value("tv show")),
                    default=Value("unknown"),
                    output_field=CharField(),
                ),
                genres=ArrayAgg("genres__name", distinct=True),
                actors=ArrayAgg(
                    "persons__full_name",
                    distinct=True,
                    filter=Q(
                        persons__personfilmwork__role__exact=PersonFilmwork.Role.ACTOR
                    ),
                ),
                directors=ArrayAgg(
                    "persons__full_name",
                    distinct=True,
                    filter=Q(
                        persons__personfilmwork__role__exact=PersonFilmwork.Role.DIRECTOR
                    ),
                ),
                writers=ArrayAgg(
                    "persons__full_name",
                    distinct=True,
                    filter=Q(
                        persons__personfilmwork__role__exact=PersonFilmwork.Role.WRITER
                    ),
                ),
            )
            .order_by("title")
        )

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context)


class MoviesListApi(MoviesApiMixin, BaseListView):
    paginate_by = 50

    def get_context_data(self, *, object_list=None, **kwargs):
        queryset = self.get_queryset()
        paginator, page, queryset, is_paginated = self.paginate_queryset(queryset, 50)
        context = {
            "count": paginator.count,
            "total_pages": paginator.num_pages,
            "prev": page.previous_page_number() if page.has_previous() else None,
            "next": page.next_page_number() if page.has_next() else None,
            "results": list(queryset),
        }
        return context


class MoviesDetailApi(MoviesApiMixin, BaseDetailView):

    def get_context_data(self, **kwargs):
        queryset = self.get_queryset()
        movie_object = self.get_object(queryset=queryset)
        return dict(movie_object)
