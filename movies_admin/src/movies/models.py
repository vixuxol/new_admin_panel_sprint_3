from django.db import models
from movies.model_mixins import UUIDMixin, TimeStampedMixin
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _


class Genre(UUIDMixin, TimeStampedMixin):
    name = models.CharField(_("name"), max_length=255)
    description = models.TextField(_("description"), blank=True)

    class Meta:
        db_table = 'content"."genre'
        verbose_name = "Жанр"
        verbose_name_plural = "Жанры"

    def __str__(self):
        return self.name


class Filmwork(UUIDMixin, TimeStampedMixin):
    class FilmworkType(models.TextChoices):
        MOVIE = "MV", _("Movie")
        TV_SHOW = "TV", _("TV Show")

    title = models.CharField(_("title"), max_length=255)
    description = models.TextField(_("description"), blank=True)
    creation_date = models.DateField(_("creation_date"), blank=True)
    rating = models.FloatField(
        _("rating"),
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    type = models.CharField(
        _("type"),
        max_length=2,
        choices=FilmworkType.choices,
        default=FilmworkType.MOVIE,
    )
    genres = models.ManyToManyField(Genre, through="GenreFilmwork")
    file_path = models.CharField(_("File path"), max_length=255, blank=True, null=True)
    persons = models.ManyToManyField("Person", through="PersonFilmwork")

    class Meta:
        db_table = 'content"."film_work'
        verbose_name = "Кинопроизведение"
        verbose_name_plural = "Кинопроизведения"

    def __str__(self):
        return self.title


class GenreFilmwork(UUIDMixin):
    film_work = models.ForeignKey("Filmwork", on_delete=models.CASCADE)
    genre = models.ForeignKey("Genre", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'content"."genre_film_work'
        unique_together = (("film_work", "genre"),)


class Person(UUIDMixin, TimeStampedMixin):
    full_name = models.CharField(_("Full Name"), max_length=255)

    class Meta:
        db_table = 'content"."person'
        verbose_name = "Участник фильма"
        verbose_name_plural = "Участники фильма"

    def __str__(self):
        return self.full_name


class PersonFilmwork(UUIDMixin):
    class Role(models.TextChoices):
        PRODUCER = "PR", _("Producer")
        ACTOR = "AC", _("Actor")
        DIRECTOR = "DR", _("Director")
        WRITER = "WR", _("Writer")

    film_work = models.ForeignKey("Filmwork", on_delete=models.CASCADE)
    person = models.ForeignKey("Person", on_delete=models.CASCADE)
    role = models.CharField(
        _("role"),
        max_length=2,
        choices=Role.choices,
        default=Role.ACTOR,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'content"."person_film_work'
        unique_together = (("film_work", "person", "role"),)
