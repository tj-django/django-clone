from itertools import repeat
from typing import List, Optional, Dict

from conditional import conditional
from django.core.checks import Error
from django.core.exceptions import ValidationError
from django.db import transaction, models, IntegrityError, connections
from django.db.models import SlugField
from django.utils.text import slugify

from model_clone.apps import ModelCloneConfig
from model_clone.utils import (
    clean_value,
    transaction_autocommit,
    get_unique_value,
    context_mutable_attribute,
)


class CloneMixin(object):
    """
    CloneMixin mixin to duplicate an object using the model cls.

    Examples:
        Using explicit fields

        class TestModel(CloneMixin, models.Model):
            field_1 = models.CharField(max_length=200)
            tags =  models.ManyToManyField(Tags)
            audiences = models.ManyToManyField(Audience)
            user = models.ForiegnKey(
                settings.AUTH_USER_MODEL,
                on_delete=models.CASCADE,
            )

            _clone_many_to_many_fields = ['tags', 'audiences']
            _clone_many_to_one_or_one_to_many_fields = ['user']
            ...

        Using implicit all except fields.

        class TestModel(CloneMixin, models.Model):
            field_1 = models.CharField(max_length=200)
            tags =  models.ManyToManyField(Tags)
            audiences = models.ManyToManyField(Audience)
            user = models.ForiegnKey(
                settings.AUTH_USER_MODEL,
                on_delete=models.CASCADE,
                null=True,
            )

            # Clones any other m2m field excluding "audiences".
            _clone_excluded_many_to_many_fields = ['audiences']
            # Clones all other fk fields excluding "user".
            _clone_excluded_many_to_one_or_one_to_many_fields = ['user']
            ...


    Attributes:
        _clone_model_fields (list): Restricted list of fields to copy from the instance.
        _clone_many_to_many_fields (list): Many to many fields (i.e TestModel.tags).
        _clone_many_to_one_or_one_to_many_fields (list): Many to one/One to many fields.
        _clone_one_to_one_fields (list): One to One fields.

        _clone_excluded_model_fields (list): Excluded model fields.
        _clone_excluded_many_to_many_fields (list): Excluded many to many fields.
        _clone_excluded_many_to_one_or_one_to_many_fields (list): Excluded m2m and
            o2m fields.
        _clone_excluded_one_to_one_fields (list): Excluded one to one fields.
    """

    # TODO: Move these to use succinct
    # names m2m_clone_fields -> many_to_many, m2o_o2m_clone_fields = []

    # Included fields
    _clone_model_fields = []
    _clone_many_to_many_fields = []
    _clone_many_to_one_or_one_to_many_fields = []
    _clone_one_to_one_fields = []

    # Excluded fields
    _clone_excluded_model_fields = []
    _clone_excluded_many_to_many_fields = []
    _clone_excluded_many_to_one_or_one_to_many_fields = []
    _clone_excluded_one_to_one_fields = []

    UNIQUE_DUPLICATE_SUFFIX = "copy"
    USE_UNIQUE_DUPLICATE_SUFFIX = True
    MAX_UNIQUE_DUPLICATE_QUERY_ATTEMPTS = 100

    @classmethod
    def _create_copy_of_instance(cls, instance):
        defaults = {}
        fields = []

        for f in instance._meta.concrete_fields:
            valid = False
            if not f.primary_key:
                if cls._clone_model_fields:
                    valid = f.name in cls._clone_model_fields
                elif cls._clone_excluded_model_fields:
                    valid = f.name not in cls._clone_excluded_model_fields
                else:
                    valid = True

            if valid:
                fields.append(f)

        unique_field_names = cls.unpack_unique_together(
            opts=instance._meta,
            only_fields=[f.attname for f in fields],
        )

        unique_fields = [
            f.name
            for f in fields
            if not f.auto_created and (f.unique or f.name in unique_field_names)
        ]

        for f in fields:
            if all(
                [
                    not f.auto_created,
                    f.concrete,
                    f.editable,
                    f not in instance._meta.related_objects,
                    f not in instance._meta.many_to_many,
                ]
            ):
                value = getattr(instance, f.attname, f.get_default())
                # Do not try to get unique value for enum type field
                if (
                    f.attname in unique_fields
                    and isinstance(f, models.CharField)
                    and not f.choices
                ):
                    value = clean_value(value, cls.UNIQUE_DUPLICATE_SUFFIX)
                    if cls.USE_UNIQUE_DUPLICATE_SUFFIX:
                        value = get_unique_value(
                            instance,
                            f.attname,
                            value,
                            cls.UNIQUE_DUPLICATE_SUFFIX,
                            f.max_length,
                            cls.MAX_UNIQUE_DUPLICATE_QUERY_ATTEMPTS,
                        )
                    if isinstance(f, SlugField):
                        value = slugify(value)
                defaults[f.attname] = value

        return cls(**defaults)

    @classmethod
    def check(cls, **kwargs):
        errors = super(CloneMixin, cls).check(**kwargs)

        if cls.USE_UNIQUE_DUPLICATE_SUFFIX and not cls.UNIQUE_DUPLICATE_SUFFIX:
            errors.append(
                Error(
                    "UNIQUE_DUPLICATE_SUFFIX is reqiured.",
                    hint=(
                        "Please provide UNIQUE_DUPLICATE_SUFFIX"
                        + "for {} or set USE_UNIQUE_DUPLICATE_SUFFIX=False".format(
                            cls.__name__
                        )
                    ),
                    obj=cls,
                    id="{}.E001".format(ModelCloneConfig.name),
                )
            )

        if all([cls._clone_model_fields, cls._clone_excluded_model_fields]):
            errors.append(
                Error(
                    "Conflicting configuration.",
                    hint=(
                        'Please provide either "_clone_model_fields"'
                        + 'or "_clone_excluded_model_fields" for {}'.format(
                            cls.__name__
                        )
                    ),
                    obj=cls,
                    id="{}.E002".format(ModelCloneConfig.name),
                )
            )

        if all(
            [cls._clone_many_to_many_fields, cls._clone_excluded_many_to_many_fields]
        ):
            errors.append(
                Error(
                    "Conflicting configuration.",
                    hint=(
                        'Please provide either "_clone_many_to_many_fields"'
                        + 'or "_clone_excluded_many_to_many_fields" for {}'.format(
                            cls.__name__
                        )
                    ),
                    obj=cls,
                    id="{}.E002".format(ModelCloneConfig.name),
                )
            )

        if all(
            [
                cls._clone_many_to_one_or_one_to_many_fields,
                cls._clone_excluded_many_to_one_or_one_to_many_fields,
            ]
        ):
            errors.append(
                Error(
                    "Conflicting configuration.",
                    hint=(
                        "Please provide either "
                        + '"_clone_many_to_one_or_one_to_many_fields"'
                        + "or "
                        + '"_clone_excluded_many_to_one'
                        + '_or_one_to_many_fields" for {}'.format(cls.__name__)
                    ),
                    obj=cls,
                    id="{}.E002".format(ModelCloneConfig.name),
                )
            )

        if all([cls._clone_one_to_one_fields, cls._clone_excluded_one_to_one_fields]):
            errors.append(
                Error(
                    "Conflicting configuration.",
                    hint=(
                        'Please provide either "_clone_one_to_one_fields"'
                        + 'or "_clone_excluded_one_to_one_fields" for {}'.format(
                            cls.__name__
                        )
                    ),
                    obj=cls,
                    id="{}.E002".format(ModelCloneConfig.name),
                )
            )

        return errors

    @transaction.atomic
    def make_clone(self, attrs=None, sub_clone=False):
        """
        Creates a clone of the django model instance.

        :param attrs (dict): Dictionary of attributes to be replaced on the cloned object.
        :param sub_clone (bool): Internal boolean used to detect cloning sub objects.
        :rtype: :obj:`django.db.models.Model`
        :return: The model instance that has been cloned.
        """
        attrs = attrs or {}
        if not self.pk:
            raise ValidationError(
                "{}: Instance must be saved before it can be cloned.".format(
                    self.__class__.__name__
                )
            )
        if sub_clone:
            duplicate = self
            duplicate.pk = None
        else:
            duplicate = self._create_copy_of_instance(self)
            # Supports only updating the attributes of the base instance.
            for name, value in attrs.items():
                setattr(duplicate, name, value)

        duplicate.save()

        one_to_one_fields = []
        many_to_one_or_one_to_many_fields = []
        many_to_many_fields = []

        for f in self._meta.related_objects:
            if f.one_to_one and f.name in self._clone_one_to_one_fields:
                one_to_one_fields.append(f)

            elif all(
                [
                    not self._clone_one_to_one_fields,
                    f.one_to_one,
                    self._clone_excluded_one_to_one_fields,
                    f not in one_to_one_fields,
                    f.name not in self._clone_excluded_one_to_one_fields,
                ]
            ):
                one_to_one_fields.append(f)

            elif all(
                [
                    any([f.many_to_one, f.one_to_many]),
                    f.name in self._clone_many_to_one_or_one_to_many_fields,
                ]
            ):
                many_to_one_or_one_to_many_fields.append(f)

            elif all(
                [
                    not self._clone_many_to_one_or_one_to_many_fields,
                    any([f.many_to_one, f.one_to_many]),
                    self._clone_excluded_many_to_one_or_one_to_many_fields,
                    f not in many_to_one_or_one_to_many_fields,
                    f.name
                    not in self._clone_excluded_many_to_one_or_one_to_many_fields,
                ]
            ):
                many_to_one_or_one_to_many_fields.append(f)

        for f in self._meta.many_to_many:
            if not sub_clone:
                if f.name in self._clone_many_to_many_fields:
                    many_to_many_fields.append(f)
                elif all(
                    [
                        not self._clone_many_to_many_fields,
                        self._clone_excluded_many_to_many_fields,
                        f.name not in self._clone_excluded_many_to_many_fields,
                        f not in many_to_many_fields,
                    ]
                ):
                    many_to_many_fields.append(f)

        # Clone one to one fields
        for field in one_to_one_fields:
            rel_object = getattr(self, field.related_name, None)
            if rel_object:
                if hasattr(rel_object, "make_clone") and callable(
                    rel_object.make_clone
                ):
                    rel_object.make_clone(
                        attrs={field.remote_field.name: duplicate}, sub_clone=True
                    )
                else:
                    rel_object.pk = None
                    setattr(rel_object, field.remote_field.name, duplicate)
                    rel_object.save()

        # Clone one to many/many to one fields
        for field in many_to_one_or_one_to_many_fields:
            items = []
            for item in getattr(self, field.related_name).all():
                try:
                    item_clone = item.make_clone(
                        attrs={field.remote_field.name: duplicate}
                    )
                except IntegrityError:
                    item_clone = item.make_clone(
                        attrs={field.remote_field.name: duplicate}, sub_clone=True
                    )
                items.append(item_clone)

            getattr(duplicate, field.related_name).set(items)

        # Clone many to many fields
        for field in many_to_many_fields:
            if all(
                [
                    field.remote_field.through,
                    not field.remote_field.through._meta.auto_created,
                ]
            ):
                objs = field.remote_field.through.objects.filter(
                    **{field.m2m_field_name(): self.pk}
                )
                for item in objs:
                    if hasattr(field.remote_field.through, "make_clone"):
                        item.make_clone(
                            attrs={field.m2m_field_name(): duplicate}, sub_clone=True
                        )
                    else:
                        item.pk = None
                        setattr(item, field.m2m_field_name(), duplicate)
                        item.save()
            else:
                source = getattr(self, field.attname)
                destination = getattr(duplicate, field.attname)
                destination.set(source.all())
        return duplicate

    @staticmethod
    def unpack_unique_together(opts, only_fields=()):
        fields = []
        for field in opts.unique_together:
            if isinstance(field, str):
                if field in only_fields:
                    fields.append(field)
            else:
                fields.extend(list([f for f in field if f in only_fields]))
        return fields

    @classmethod
    def bulk_clone_multi(cls, objs, attrs=None, batch_size=None):
        # type: (List[models.Model], Optional[List[Dict]], Optional[int]) -> List[models.Model]
        # TODO: Support bulk clones split by the batch_szie
        pass

    def bulk_clone(self, count, attrs=None, batch_size=None, auto_commit=False):
        ops = connections[self.__class__._default_manager.db].ops
        objs = range(count)
        clones = []
        batch_size = batch_size or max(ops.bulk_batch_size([], list(objs)), 1)

        with conditional(
            auto_commit,
            transaction_autocommit(using=self.__class__._default_manager.db),
        ):
            # If count exceeds the MAX_UNIQUE_DUPLICATE_QUERY_ATTEMPTS
            with conditional(
                self.MAX_UNIQUE_DUPLICATE_QUERY_ATTEMPTS < count,
                context_mutable_attribute(
                    self,
                    "MAX_UNIQUE_DUPLICATE_QUERY_ATTEMPTS",
                    count,
                ),
            ):
                if not self.MAX_UNIQUE_DUPLICATE_QUERY_ATTEMPTS >= count:
                    raise AssertionError(
                        "An Unknown error has occured: Expected ({}) >= ({})".format(
                            self.MAX_UNIQUE_DUPLICATE_QUERY_ATTEMPTS, count
                        ),
                    )
                clones = list(repeat(self.make_clone(attrs=attrs), batch_size))

        return clones

    def parallel_clone(self, count, attrs=None, batch_size=None, auto_commit=False):
        # if this takes n time for t records
        # t^n i.e 100 * 10ms = 1000ms to clone 100 objects.
        # I'll like to reduce this down to max time to clone count/batch_size i.e
        # If it take 100ms to clone 100 objects with a db of batch_size 100
        # If it takes 10ms to clone 10 objects i'll like to keep this down to 10ms for
        # max_num_of_threads i.e 10 threads for 100 objects.
        # This should run in parallel
        # Testing jit and cpython if they offer better API's.
        pass
