from django.core.exceptions import ValidationError
from django.db import models


def create_copy_of_instance(instance, exclude=(), save_new=True, attrs=()):
    """
    Clone an instance of `django.db.models.Model`.

    Args:
        instance(django.db.models.Model): The model instance to clone.
        exclude(list|set): List or set of fields to exclude from unique validation.
        **attrs: Kwargs of field and value to set on the duplicated instance.

    Returns:
        (django.db.models.Model): The new duplicated instance.

    Examples:
        >>> from django.contrib.auth import get_user_model
        >>> from sample.models import Book
        >>> user = get_user_model().objects.create()
        >>> instance = Book.objects.get(pk=1)
        >>> instance.pk
        1
        >>> instance.name
        "The Beautiful Life"
        >>> duplicate.pk
        2
        >>> duplicate.name
        "Duplicate Book 2"
    """

    defaults = {}
    attrs = attrs or {}
    fields = instance.__class__._meta.concrete_fields

    if not isinstance(instance, models.Model):
        raise ValueError('Invalid: Expected an instance of django.db.models.Model')

    if not isinstance(attrs, dict):
        try:
            attrs = dict(attrs)
        except (TypeError, ValueError):
            raise ValueError('Invalid: Expected attrs to be a dict or iterable.')

    for f in fields:
        if all([
            not f.auto_created,
            f.concrete,
            f.editable,
            f not in instance.__class__._meta.related_objects,
            f not in instance.__class__._meta.many_to_many,
        ]):
            defaults[f.attname] = getattr(instance, f.attname, f.get_default())
    defaults.update(attrs)

    new_obj = instance.__class__(**defaults)

    exclude = exclude or [
        f.name for f in instance._meta.fields
        if any([
            f.name not in defaults,
            f.has_default(),
            f.null,
        ])
    ]

    try:
        # Run the unique validation before creating the instance.
        new_obj.full_clean(exclude=exclude)
    except ValidationError as e:
        raise ValidationError(', '.join(e.messages))

    if save_new:
        new_obj.save()

    return new_obj
