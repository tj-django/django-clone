import contextlib
import re

import six
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.transaction import TransactionManagementError


def create_copy_of_instance(instance, exclude=(), save_new=True, attrs=None):
    """
    Clone an instance of `django.db.models.Model`.

    Args:
        instance(django.db.models.Model): The model instance to clone.
        exclude(list|set): List or set of fields to exclude from unique validation.
        save_new(bool): Save the model instance after duplication calling .save().
        attrs(dict): Kwargs of field and value to set on the duplicated instance.

    Returns:
        (django.db.models.Model): The new duplicated instance.

    Examples:
        >>> from django.contrib.auth import get_user_model
        >>> from sample.models import Book
        >>> instance = Book.objects.create(name='The Beautiful Life')
        >>> instance.pk
        1
        >>> instance.name
        "The Beautiful Life"
        >>> duplicate = instance.make_clone(attrs={'name': 'Duplicate Book 2'})
        >>> duplicate.pk
        2
        >>> duplicate.name
        "Duplicate Book 2"
    """

    defaults = {}
    attrs = attrs or {}
    fields = instance.__class__._meta.concrete_fields

    if not isinstance(instance, models.Model):
        raise ValueError("Invalid: Expected an instance of django.db.models.Model")

    if not isinstance(attrs, dict):
        try:
            attrs = dict(attrs)
        except (TypeError, ValueError):
            raise ValueError("Invalid: Expected attrs to be a dict or iterable.")

    for f in fields:
        if all(
            [
                not f.auto_created,
                f.concrete,
                f.editable,
                f not in instance.__class__._meta.related_objects,
                f not in instance.__class__._meta.many_to_many,
            ]
        ):
            defaults[f.attname] = getattr(instance, f.attname, f.get_default())
    defaults.update(attrs)

    new_obj = instance.__class__(**defaults)

    exclude = exclude or [
        f.name
        for f in instance._meta.fields
        if any([f.name not in defaults, f.has_default(), f.null])
    ]

    try:
        # Run the unique validation before creating the instance.
        new_obj.full_clean(exclude=exclude)
    except ValidationError as e:
        raise ValidationError(", ".join(e.messages))

    if save_new:
        new_obj.save()

    return new_obj


def clean_value(value, suffix):
    # type: (str, str) -> str
    return re.sub(r"\s{}\s[\d]$".format(suffix), "", value, flags=re.I)


@contextlib.contextmanager
def transaction_autocommit(using=None):
    try:
        transaction.set_autocommit(True, using=using)
        yield
    except TransactionManagementError:
        raise


@contextlib.contextmanager
def context_mutable_attribute(obj, key, value):
    default = None
    is_set = hasattr(obj, key)
    if is_set:
        default = getattr(obj, key)
    try:
        setattr(obj, key, value)
        yield
    finally:
        if not is_set and hasattr(obj, key):
            del obj[key]
        else:
            setattr(obj, key, default)


def get_value(value, suffix, max_length, index):
    duplicate_suffix = " {} {}".format(suffix, index)
    total_length = len(value + duplicate_suffix)

    if total_length > max_length:
        # Truncate the value to max_length - suffix length.
        value = value[: max_length - len(duplicate_suffix)]

    return "{}{}".format(value, duplicate_suffix)


def generate_value(value, suffix, max_length, max_attempts):
    yield get_value(value, suffix, max_length, 1)

    for i in range(1, max_attempts):
        yield get_value(value, suffix, max_length, i)

    raise StopIteration(
        "CloneError: max unique attempts for {} exceeded ({})".format(
            value, max_attempts
        )
    )


def get_unique_value(obj, fname, value, suffix, max_length, max_attempts):
    qs = obj.__class__._default_manager.all()
    it = generate_value(value, suffix, max_length, max_attempts)

    new = six.next(it)
    kwargs = {fname: new}

    while qs.filter(**kwargs).exists():
        new = six.next(it)
        kwargs[fname] = new

    return new
