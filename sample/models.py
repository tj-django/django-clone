from uuid import uuid4

import django
from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext as _

from model_clone.utils import get_unique_default

if django.VERSION >= (2, 2):
    from django.db.models import UniqueConstraint

from model_clone import CloneMixin
from model_clone.models import CloneModel


class Author(CloneModel):
    first_name = models.CharField(max_length=200, blank=True, unique=True)
    last_name = models.CharField(default="Unknown", max_length=200, blank=True)
    age = models.PositiveIntegerField()

    uuid = models.UUIDField(default=uuid4, unique=True, editable=False)

    SEX_CHOICES = [
        ("U", "Unknown"),
        ("F", "Female"),
        ("M", "Male"),
    ]
    sex = models.CharField(choices=SEX_CHOICES, max_length=1, default="U")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
    )

    lives_in = models.ForeignKey("House", on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return _("{} {}".format(self.first_name, self.last_name))

    @property
    def full_name(self):
        return "{} {}".format(self.first_name, self.last_name)

    class Meta:
        unique_together = (("first_name", "last_name", "sex"),)


def get_unique_tag_name():
    return get_unique_default(
        model=Tag,
        fname="name",
        value="test-tag",
    )


class Tag(CloneModel):
    name = models.CharField(
        max_length=255, default=get_unique_tag_name, unique=django.VERSION < (2, 2)
    )

    if django.VERSION >= (2, 2):

        class Meta:
            constraints = [
                UniqueConstraint(fields=["name"], name="tag_unique_name"),
            ]

    def __str__(self):
        return _(self.name)


class SaleTag(CloneModel):
    name = models.CharField(max_length=255, unique=django.VERSION < (2, 2))

    if django.VERSION >= (2, 2):

        class Meta:
            constraints = [
                UniqueConstraint(fields=["name"], name="sale_tag_unique_name"),
            ]

    def __str__(self):
        return _(self.name)


class Book(CloneModel):
    name = models.CharField(max_length=2000)
    slug = models.SlugField(unique=True)
    custom_slug = models.SlugField(default="")
    authors = models.ManyToManyField(Author, related_name="books")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    tags = models.ManyToManyField(Tag, through="BookTag")
    sale_tags = models.ManyToManyField(SaleTag, through="BookSaleTag")
    published_at = models.DateTimeField(null=True, blank=True, default=timezone.now)

    found_in = models.ForeignKey(
        "Furniture", on_delete=models.SET_NULL, null=True, related_name="books"
    )

    def __str__(self):
        return _(self.name)

    def pre_save_duplicate(self, instance):
        instance.name = self.name

        return instance


class BookTag(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.PROTECT)

    class Meta:
        unique_together = [
            ("book", "tag"),
        ]


class BookSaleTag(CloneModel):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    sale_tag = models.ForeignKey(SaleTag, on_delete=models.PROTECT)

    class Meta:
        unique_together = [
            ("book", "sale_tag"),
        ]


class Page(CloneModel):
    content = models.CharField(max_length=20000)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)


class Edition(CloneModel):
    seq = models.PositiveIntegerField()
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="editions")
    created_at = models.DateTimeField(default=timezone.now)


class Library(CloneModel):
    id = models.UUIDField(primary_key=True, default=uuid4)
    name = models.CharField(max_length=100)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)

    uuid = models.UUIDField(default=uuid4, unique=True, editable=False)

    _clone_fields = ["name"]
    _clone_o2o_fields = ["user"]

    class Meta:
        verbose_name_plural = _("libraries")

    def __str__(self):
        return _(self.name)


class Assignment(CloneMixin, models.Model):
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    title = models.CharField(
        max_length=100, default="", blank=True, verbose_name=_("Job title")
    )
    assignment_date = models.DateField(blank=True, null=True)
    company = models.ForeignKey(
        "sample_company.CompanyDepot",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        verbose_name=_("Company"),
    )
    applied_drivers = models.ManyToManyField(
        "sample_driver.Driver",
        blank=True,
        verbose_name=_("Driver applications"),
        related_name="driver_applications",
    )
    chosen_drivers = models.ManyToManyField(
        "sample_driver.Driver",
        blank=True,
        verbose_name=_("Chosen drivers"),
    )

    contract = models.ForeignKey(
        "sample_assignment.Contract",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name=_("Choose contract"),
        related_name="assignment_contracts",
    )

    ASSIGNMENT_STATUS = [
        (1, "Complete"),
        (2, "Incomplete"),
    ]

    assignment_status = models.CharField(
        max_length=2,
        choices=ASSIGNMENT_STATUS,
        default="O",
        verbose_name=_("Assignment status"),
        blank=True,
    )
    location = models.CharField(max_length=25, default="", verbose_name=_("Location"))

    DRIVER_TYPES = [
        (1, "Commercial"),
        (2, "Residential"),
    ]

    driver_type = models.CharField(
        max_length=2, choices=DRIVER_TYPES, default="", verbose_name=_("Driver type")
    )
    CAR_TYPES = [
        (1, "Large"),
        (2, "Small"),
    ]
    car_type = models.CharField(
        max_length=2, choices=CAR_TYPES, default="", verbose_name=_("Car type")
    )
    compensation = models.DecimalField(
        null=True, max_digits=5, decimal_places=2, verbose_name=_("Compensation")
    )
    hours = models.IntegerField(verbose_name=_("Amount of hours"))
    spots_available = models.IntegerField(null=True, verbose_name=_("Spots available"))
    description = models.TextField(blank=True, verbose_name=_("Assignment description"))

    # Model clone settings
    _clone_excluded_m2m_fields = ["applied_drivers", "chosen_drivers"]

    class Meta:
        verbose_name = _("Assigment")
        verbose_name_plural = _("Assignments")

    def __str__(self):
        return self.title


class House(CloneMixin, models.Model):
    name = models.CharField(max_length=255)

    _clone_fields = ["name"]
    _clone_m2o_or_o2m_fields = ["rooms"]

    def __str__(self):
        return self.name


class Room(CloneMixin, models.Model):
    name = models.CharField(max_length=255)

    house = models.ForeignKey(House, related_name="rooms", on_delete=models.CASCADE)

    _clone_fields = ["name"]
    _clone_m2o_or_o2m_fields = ["furniture"]

    def __str__(self):
        return self.name


class Furniture(CloneMixin, models.Model):
    name = models.CharField(max_length=255)

    room = models.ForeignKey(Room, related_name="furniture", on_delete=models.PROTECT)

    _clone_fields = ["name"]

    def __str__(self):
        return self.name


class Cover(CloneModel):
    content = models.CharField(max_length=200)
    book = models.OneToOneField(Book, on_delete=models.CASCADE)


class BackCover(models.Model):
    content = models.CharField(max_length=200)
    book = models.OneToOneField(Book, on_delete=models.CASCADE)


class Product(CloneMixin, models.Model):
    name = models.TextField(unique=True)


class Sentence(CloneMixin, models.Model):
    value = models.TextField()

    _clone_o2o_fields = {"ending"}


class Ending(CloneMixin, models.Model):
    sentence = models.OneToOneField(
        Sentence, on_delete=models.CASCADE, related_name="ending"
    )
