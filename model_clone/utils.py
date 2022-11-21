import contextlib
import re

import six
from django.db import models, transaction
from django.db.transaction import TransactionManagementError


def create_copy_of_instance(
    instance, attrs=None, exclude=(), save_new=True, using=None
):
    """
    Clone an instance of `django.db.models.Model`.

    :param instance: The model instance to clone.
    :type instance: django.db.models.Model
    :param exclude: List or set of fields to exclude from unique validation.
    :type exclude: list|set
    :param save_new: Save the model instance after duplication calling .save().
    :type save_new: bool
    :param using: The database alias used to save the created instances.
    :type using: str
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
    default_db_alias = instance._state.db or instance.__class__._default_manager.db
    using = using or default_db_alias
    fields = instance.__class__._meta.concrete_fields

    if not isinstance(attrs, dict):
        try:
            attrs = dict(attrs)
        except (TypeError, ValueError):
            raise ValueError(
                "Invalid: Expected attrs to be a dict or iterable of key and value tuples."
            )

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

    exclude = set(
        [
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
        + list(exclude)
    )

    # Bug with django using full_clean on a different db
    if using == default_db_alias:
        # Validate the new instance on the same database
        new_obj.full_clean(exclude=exclude)

    if save_new:
        new_obj.save(using=using)

    return new_obj


def unpack_unique_constraints(opts, only_fields=()):
    """
    Unpack unique constraint fields.

    :param opts: Model options
    :type opts: `django.db.models.options.Options`
    :param only_fields: Fields that should be considered.
    :type only_fields: `collections.Iterable`
    :return: Flat list of fields.
    """
    fields = []
    constraints = getattr(
        opts, "total_unique_constraints", getattr(opts, "constraints", [])
    )
    for constraint in constraints:
        fields.extend([f for f in constraint.fields if f in only_fields])
    return fields


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
    :rtype: `str`
    """
    # type: (str, str) -> str
    return re.sub(r"([\s-]?){}[\s-][\d]$".format(suffix), "", value, flags=re.I)


@contextlib.contextmanager
def transaction_autocommit(using=None):
    """
    Context manager to enable autocommit.

    :param using: The database alias used to save the created instances.
    :type using: str
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

    :param obj: The object to modify.
    :type obj: `object`
    :param key: The attribute name to modify.
    :type key: `str`
    :param value: The value to set on the attribute.
    :type value: `object`
    """
    attribute_exists = hasattr(obj, key)
    default = getattr(obj, key, None)
    try:
        setattr(obj, key, value)
        yield
    finally:
        if attribute_exists:
            setattr(obj, key, default)
        else:
            delattr(obj, key)  # pragma: no cover


def get_value(value, suffix, transform, max_length, index=None):
    """
    Append a suffix to a string value and pass it directly to a
    transformation function.

    :param value: Current value e.g "Test Copy" or "test-copy" for slug fields.
    :type value: `str`
    :param suffix: The suffix value to be replaced with an empty string.
    :type suffix: `str`
    :param transform: The transformation function to apply to the value.
    :type transform: `callable`
    :param max_length: The maximum length of the value.
    :type max_length: `int`
    :param index: The index of the copy.
    :type index: `int`
    :return: The transformed value.
    """
    if index is None:
        duplicate_suffix = " {}".format(suffix.strip())
    else:
        duplicate_suffix = " {} {}".format(suffix.strip(), index)

    total_length = len(value + duplicate_suffix)

    if max_length is not None and total_length > max_length:
        # Truncate the value to max_length - suffix length.
        value = value[: max_length - len(duplicate_suffix)]

    return transform("{}{}".format(value, duplicate_suffix))


def generate_value(value, suffix, transform, max_length, max_attempts):
    """
    Given a fixed max attempt generate a unique value.

    :param value: Current value e.g "Test Copy" or "test-copy" for slug fields.
    :type value: `str`
    :param suffix: The suffix value to be replaced with an empty string.
    :type suffix: `str`
    :param transform: The transformation function to apply to the value.
    :type transform: `callable`
    :param max_length: The maximum length of the value.
    :type max_length: `int`
    :param max_attempts: The maximum number of attempts to generate a unique value.
    :type max_attempts: `int`
    :return: The unique value.
    """

    for i in range(1, max_attempts):
        yield get_value(value, suffix, transform, max_length, i)

    raise StopIteration(
        "CloneError: max unique attempts for {} exceeded ({})".format(
            value, max_attempts
        )
    )


def get_unique_value(
    model,
    fname,
    value="",
    transform=lambda v: v,
    suffix="",
    max_length=None,
    max_attempts=100,
    using=None,
):
    """
    Generate a unique value using current value and query the model
    for existing objects with the new value.
    """
    qs = model._default_manager.using(using or model._default_manager.db).all()

    if not qs.filter(**{fname: value}).exists():
        return value

    it = generate_value(value, suffix, transform, max_length, max_attempts)
    new = six.next(it)
    kwargs = {fname: new}

    while qs.filter(**kwargs).exists():
        new = six.next(it)
        kwargs[fname] = new

    return new


def get_fields_and_unique_fields_from_cls(
    model,
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

    for f in model._meta.concrete_fields:
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
                valid = f.name not in clone_excluded_o2o_fields  # pragma: no cover
            else:
                valid = True

        if valid:
            fields.append(f)

    unique_field_names = unpack_unique_together(
        opts=model._meta,
        only_fields=[f.attname for f in fields],
    )

    unique_constraint_field_names = unpack_unique_constraints(
        opts=model._meta,
        only_fields=[f.attname for f in fields],
    )

    unique_fields = [
        f.name
        for f in fields
        if not f.auto_created
        and (
            f.unique
            or f.name in unique_field_names
            or f.name in unique_constraint_field_names
        )
    ]

    return fields, unique_fields


def get_unique_default(
    model,
    fname,
    value,
    transform=lambda v: v,
    suffix="",
    max_length=None,
    max_attempts=100,
):
    """Get a unique value using the value and adding a suffix if needed."""

    qs = model._default_manager.all()

    if not qs.filter(**{fname: value}).exists():
        return value

    it = generate_value(
        value,
        suffix,
        transform,
        max_length,
        max_attempts,
    )

    new = six.next(it)
    kwargs = {fname: new}

    while qs.filter(**kwargs).exists():
        new = six.next(it)
        kwargs[fname] = new

    return new
