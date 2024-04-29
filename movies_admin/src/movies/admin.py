from django.contrib import admin
from movies.models import Genre, Filmwork, GenreFilmwork, PersonFilmwork, Person


class GenreFilmworkInline(admin.TabularInline):
    model = GenreFilmwork


class PersonFilmworkInline(admin.TabularInline):
    model = PersonFilmwork


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at")
    search_fields = ("name", "id")


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ("full_name", "created_at")
    search_fields = ("full_name", "id")


@admin.register(Filmwork)
class FilmworkAdmin(admin.ModelAdmin):
    inlines = (GenreFilmworkInline, PersonFilmworkInline)

    list_display = (
        "title",
        "type",
        "creation_date",
        "rating",
    )
    list_filter = ("type",)
    search_fields = ("title", "description", "id")
