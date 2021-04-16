import contextlib
import re

import six
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.db.transaction import TransactionManagementError


def create_copy_of_instance(instance, exclude=(), save_new=True, attrs=None):
    """
    Clone an instance of `django.db.models.Model`.

    :param instance: The model instance to clone.
    :type instance: django.db.models.Model
    :param exclude: List or set of fields to exclude from unique validation.
    :type exclude: list|set
    :param save_new: Save the model instance after duplication calling .save().
    :type save_new: bool
    :param attrs: Kwargs of field and value to set on the duplicated instance.
    :type attrs: dict
    :return: The new duplicated instance.
    :rtype: django.db.models.Model

    :example:
    >>> from django.contrib.auth import get_user_model
    >>> from sample.models import Book
    >>> instance = Book.objects.create(name='The Beautiful Life')
    >>> instance.pk
    1
    >>> instance.name
    "The Beautiful Life"
    >>> duplicate = create_copy_of_instance(instance, attrs={'name': 'Duplicate Book 2'})
    >>> duplicate.pk
    2
    >>> duplicate.name
    "Duplicate Book 2"
    """

    if not isinstance(instance, models.Model):
        raise ValueError("Invalid: Expected an instance of django.db.models.Model")

    defaults = {}
    attrs = attrs or {}
    fields = instance.__class__._meta.concrete_fields

    if not isinstance(attrs, dict):
        try:
            attrs = dict(attrs)
        except (TypeError, ValueError):
            raise ValueError("Invalid: Expected attrs to be a dict or iterable.")

    for f in fields:
        if all(
            [
                not f.auto_created,
                not f.primary_key,
                f.concrete,
                f.editable,
                f not in instance.__class__._meta.related_objects,
                f not in instance.__class__._meta.many_to_many,
            ]
        ):
            # Prevent duplicates
            if f.name not in attrs:
                defaults[f.attname] = getattr(instance, f.attname, f.get_default())

    defaults.update(attrs)

    new_obj = instance.__class__(**defaults)

    exclude = exclude or [
        f.name
        for f in instance._meta.fields
        if any(
            [
                all([f.name not in defaults, f.attname not in defaults]),
                f.has_default(),
                f.null,
            ]
        )
    ]

    try:
        # Run the unique validation before creating the instance.
        new_obj.full_clean(exclude=exclude)
    except ValidationError as e:
        raise ValidationError(", ".join(e.messages))

    if save_new:
        new_obj.save()

    return new_obj


def unpack_unique_together(opts, only_fields=()):
    """
    Unpack unique together fields.

    :param opts: Model options
    :type opts: `django.db.models.options.Options`
    :param only_fields: Fields that should be considered.
    :type only_fields: `collections.Iterable`
    :return: Flat list of fields.
    """
    fields = []
    for field in opts.unique_together:
        fields.extend(list([f for f in field if f in only_fields]))
    return fields


def clean_value(value, suffix):
    """
    Strip out copy suffix from a string value.

    :param value: Current value e.g "Test Copy" or "test-copy" for slug fields.
    :type value: `str`
    :param suffix: The suffix value to be replaced with an empty string.
    :type suffix: `str`
    :return: Stripped string without the suffix.
    """
    # type: (str, str) -> str
    return re.sub(r"([\s-]?){}[\s-][\d]$".format(suffix), "", value, flags=re.I)


@contextlib.contextmanager
def transaction_autocommit(using=None):
    """
    Context manager with autocommit enabled.
    """
    try:
        transaction.set_autocommit(True, using=using)
        yield
    except TransactionManagementError:
        raise


@contextlib.contextmanager
def context_mutable_attribute(obj, key, value):
    """
    Context manager that modifies an obj temporarily.
    """
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


def get_value(value, suffix, transform, max_length, index):
    """
    Append a suffix to a string value and apply a pass directly to a
    transformation function.
    """
    duplicate_suffix = " {} {}".format(suffix, index)
    total_length = len(value + duplicate_suffix)

    if total_length > max_length:
        # Truncate the value to max_length - suffix length.
        value = value[: max_length - len(duplicate_suffix)]

    return transform("{}{}".format(value, duplicate_suffix))


def generate_value(value, suffix, transform, max_length, max_attempts):
    """
    Given a fixed max attempt generate a unique value.
    """
    yield get_value(value, suffix, transform, max_length, 1)

    for i in range(1, max_attempts):
        yield get_value(value, suffix, transform, max_length, i)

    raise StopIteration(
        "CloneError: max unique attempts for {} exceeded ({})".format(
            value, max_attempts
        )
    )


def get_unique_value(obj, fname, value, transform, suffix, max_length, max_attempts):
    """
    Generate a unique value using current value and query the model
    for existing objects with the new value.
    """
    qs = obj.__class__._default_manager.all()
    it = generate_value(value, suffix, transform, max_length, max_attempts)

    new = six.next(it)
    kwargs = {fname: new}

    while qs.filter(**kwargs).exists():
        new = six.next(it)
        kwargs[fname] = new

    return new


def get_fields_and_unique_fields_from_cls(
    cls,
    force,
    clone_fields,
    clone_excluded_fields,
    clone_o2o_fields,
    clone_excluded_o2o_fields,
):
    """Get a list of all fields and unique fields from a model class.

    Skip the clone_* properties if force is ``True``.
    """
    fields = []

    for f in cls._meta.concrete_fields:
        valid = False
        if not getattr(f, "primary_key", False):
            if clone_fields and not force and not getattr(f, "one_to_one", False):
                valid = f.name in clone_fields
            elif (
                clone_excluded_fields
                and not force
                and not getattr(f, "one_to_one", False)
            ):
                valid = f.name not in clone_excluded_fields
            elif clone_o2o_fields and not force and getattr(f, "one_to_one", False):
                valid = f.name in clone_o2o_fields
            elif (
                clone_excluded_o2o_fields
                and not force
                and getattr(f, "one_to_one", False)
            ):
                valid = f.name not in clone_excluded_o2o_fields
            else:
                valid = True

        if valid:
            fields.append(f)

    unique_field_names = unpack_unique_together(
        opts=cls._meta,
        only_fields=[f.attname for f in fields],
    )

    unique_fields = [
        f.name
        for f in fields
        if not f.auto_created and (f.unique or f.name in unique_field_names)
    ]

    return fields, unique_fields
