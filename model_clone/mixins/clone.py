from itertools import repeat, chain
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
    unpack_unique_together, get_excluded_fields,
)


class CloneMixin(object):

    """
    CloneMixin mixin to duplicate an object using the model cls.

    :param _clone_fields: Restricted List of fields to copy from the instance.
    :type _clone_fields`collections.Iterable`
    :param _clone_m2m_fields: Many to many fields (Example: TestModel.tags).
    :type _clone_m2m_fields`collections.Iterable`
    :param _clone_m2o_or_o2m_fields: Many to one/One to many fields.
    :type _clone_m2o_or_o2m_fields`collections.Iterable`
    :param _clone_o2o_fields: One to One fields.
    :type _clone_o2o_fields`collections.Iterable`

    :param _clone_excluded_fields: Excluded model fields.
    :type _clone_excluded_fields`collections.Iterable`
    :param _clone_excluded_m2m_fields: Excluded many to many fields.
    :type _clone_excluded_m2m_fields`collections.Iterable`
    :param _clone_excluded_m2o_or_o2m_fields: Excluded many to many
        and one to many fields.
    :type _clone_excluded_m2o_or_o2m_fields`collections.Iterable`
    :param _clone_excluded_o2o_fields: Excluded one to one fields.
    :type _clone_excluded_o2o_fields: `collections.Iterable`

    :Example:
    >>> # Using explicit fields
    >>>
    >>> class TestModel(CloneMixin, models.Model):
    >>>     field_1 = models.CharField(max_length=200)
    >>>     tags =  models.ManyToManyField(Tags)
    >>>     audiences = models.ManyToManyField(Audience)
    >>>     user = models.ForiegnKey(
    >>>         settings.AUTH_USER_MODEL,
    >>>         on_delete=models.CASCADE,
    >>>     )

    >>>     _clone_m2m_fields = ['tags', 'audiences']
    >>>     _clone_m2o_or_o2m_fields = ['user']
    >>>     ...

    >>> # Using implicit all except fields.

    >>> class TestModel(CloneMixin, models.Model):
    >>>     field_1 = models.CharField(max_length=200)
    >>>     tags =  models.ManyToManyField(Tags)
    >>>     audiences = models.ManyToManyField(Audience)
    >>>     user = models.ForiegnKey(
    >>>         settings.AUTH_USER_MODEL,
    >>>         on_delete=models.CASCADE,
    >>>         null=True,
    >>>     )

    >>>     # Clones any other m2m field excluding "audiences".
    >>>     _clone_excluded_m2m_fields = ['audiences']
    >>>     # Clones all other many to one or one to many fields excluding "user".
    >>>     _clone_excluded_m2o_or_o2m_fields = ['user']
    >>>     ...
    """

    # Included fields
    _clone_fields = []  # type: List[str]
    _clone_m2m_fields = []  # type: List[str]
    _clone_m2o_or_o2m_fields = []  # type: List[str]
    _clone_o2o_fields = []  # type: List[str]

    # Excluded fields
    _clone_excluded_fields = []  # type: List[str]
    _clone_excluded_m2m_fields = []  # type: List[str]
    _clone_excluded_m2o_or_o2m_fields = []  # type: List[str]
    _clone_excluded_o2o_fields = []  # type: List[str]

    UNIQUE_DUPLICATE_SUFFIX = "copy"  # type: str
    USE_UNIQUE_DUPLICATE_SUFFIX = True  # type: bool
    MAX_UNIQUE_DUPLICATE_QUERY_ATTEMPTS = 100  # type: int

    @staticmethod
    def _create_copy_of_instance(instance, force=False):
        """
        Create a copy of an instance

        :param instance: The instance to be duplicated.
        :type instance: `django.db.models.Model`
        :param force: Flag to skip using the current model clone declared attributes.
        :type force: bool
        :return: A new transient instance.
        :rtype: `django.db.models.Model`
        """
        cls = instance.__class__
        clone_fields = getattr(cls, "_clone_fields", CloneMixin._clone_fields)
        clone_excluded_fields = getattr(
            cls, "_clone_excluded_fields", CloneMixin._clone_excluded_fields
        )
        unique_duplicate_suffix = getattr(
            cls, "UNIQUE_DUPLICATE_SUFFIX", CloneMixin.UNIQUE_DUPLICATE_SUFFIX
        )
        use_unique_duplicate_suffix = getattr(
            cls,
            "USE_UNIQUE_DUPLICATE_SUFFIX",
            CloneMixin.USE_UNIQUE_DUPLICATE_SUFFIX,
        )
        max_unique_duplicate_query_attempts = getattr(
            cls,
            "MAX_UNIQUE_DUPLICATE_QUERY_ATTEMPTS",
            CloneMixin.MAX_UNIQUE_DUPLICATE_QUERY_ATTEMPTS,
        )

        fields = []

        for f in instance._meta.concrete_fields:
            valid = False
            if not f.primary_key:
                if clone_fields and not force:
                    valid = f.name in clone_fields
                elif clone_excluded_fields and not force:
                    valid = f.name not in clone_excluded_fields
                else:
                    valid = True

            if valid:
                fields.append(f)

        unique_field_names = unpack_unique_together(
            opts=instance._meta,
            only_fields=[f.attname for f in fields],
        )

        unique_fields = [
            f.name
            for f in fields
            if not f.auto_created and (f.unique or f.name in unique_field_names)
        ]

        new_instance = cls()

        for f in fields:
            value = getattr(instance, f.attname, f.get_default())

            if isinstance(f, (models.DateTimeField, models.DateField)):
                if f.auto_now or f.auto_now_add:
                    f.pre_save(new_instance, add=True)
                    continue

            if all(
                [
                    not f.auto_created,
                    f.concrete,
                    f.editable,
                    not isinstance(f, (models.DateTimeField, models.DateField)),
                    f not in instance._meta.related_objects,
                    f not in instance._meta.many_to_many,
                    f.name in unique_fields,
                ]
            ):
                value = getattr(instance, f.attname, f.get_default())

                # Do not try to get unique value for enum type field
                if isinstance(f, models.CharField) and not f.choices:
                    value = clean_value(value, unique_duplicate_suffix)
                    if use_unique_duplicate_suffix:
                        value = get_unique_value(
                            obj=instance,
                            fname=f.attname,
                            value=value,
                            transform=(slugify if isinstance(f, SlugField) else str),
                            suffix=unique_duplicate_suffix,
                            max_length=f.max_length,
                            max_attempts=max_unique_duplicate_query_attempts,
                        )

            setattr(new_instance, f.attname, value)

        return new_instance

    @classmethod
    def check(cls, **kwargs):
        errors = super(CloneMixin, cls).check(**kwargs)

        if cls.USE_UNIQUE_DUPLICATE_SUFFIX and not cls.UNIQUE_DUPLICATE_SUFFIX:
            errors.append(
                Error(
                    "UNIQUE_DUPLICATE_SUFFIX is required.",
                    hint=(
                        "Please provide UNIQUE_DUPLICATE_SUFFIX"
                        + " for {} or set USE_UNIQUE_DUPLICATE_SUFFIX=False".format(
                            cls.__name__
                        )
                    ),
                    obj=cls,
                    id="{}.E001".format(ModelCloneConfig.name),
                )
            )

        if all([cls._clone_fields, cls._clone_excluded_fields]):
            errors.append(
                Error(
                    "Conflicting configuration.",
                    hint=(
                        'Please provide either "_clone_fields"'
                        + ' or "_clone_excluded_fields" for model {}'.format(
                            cls.__name__
                        )
                    ),
                    obj=cls,
                    id="{}.E002".format(ModelCloneConfig.name),
                )
            )

        if all([cls._clone_m2m_fields, cls._clone_excluded_m2m_fields]):
            errors.append(
                Error(
                    "Conflicting configuration.",
                    hint=(
                        'Please provide either "_clone_m2m_fields"'
                        + ' or "_clone_excluded_m2m_fields" for model {}'.format(
                            cls.__name__
                        )
                    ),
                    obj=cls,
                    id="{}.E002".format(ModelCloneConfig.name),
                )
            )

        if all(
            [
                cls._clone_m2o_or_o2m_fields,
                cls._clone_excluded_m2o_or_o2m_fields,
            ]
        ):
            errors.append(
                Error(
                    "Conflicting configuration.",
                    hint=(
                        "Please provide either "
                        + '"_clone_m2o_or_o2m_fields"'
                        + " or "
                        + '"_clone_excluded_m2o_or_o2m_fields" for {}'.format(
                            cls.__name__
                        )
                    ),
                    obj=cls,
                    id="{}.E002".format(ModelCloneConfig.name),
                )
            )

        if all([cls._clone_o2o_fields, cls._clone_excluded_o2o_fields]):
            errors.append(
                Error(
                    "Conflicting configuration.",
                    hint=(
                        'Please provide either "_clone_o2o_fields"'
                        + ' or "_clone_excluded_o2o_fields" for {}'.format(cls.__name__)
                    ),
                    obj=cls,
                    id="{}.E002".format(ModelCloneConfig.name),
                )
            )

        return errors

    def __duplicate_o2o_fields(self, duplicate):
        """
        Duplicate the one to one fields.

        :param duplicate: The transient instance that should be duplicated.
        :type duplicate: `django.db.models.Model`
        :return: The duplicate instance with all the one to one fields duplicated.
        """
        fields = set()

        if self._clone_o2o_fields or self._clone_excluded_o2o_fields:
            for f in chain(self._meta.related_objects, self._meta.concrete_fields):
                if any(
                    [
                        f.one_to_one and f.name in self._clone_o2o_fields,
                        f.one_to_one
                        and self._clone_excluded_o2o_fields
                        and f.name not in self._clone_excluded_o2o_fields,
                    ]
                ):
                    fields.add(f)

        # Clone one to one fields
        for field in fields:
            rel_object = getattr(self, field.name, None)
            if rel_object:
                if hasattr(rel_object, "make_clone") and callable(
                    rel_object.make_clone
                ):
                    try:
                        new_rel_object = rel_object.make_clone()
                    except IntegrityError:
                        new_rel_object = rel_object.make_clone(sub_clone=True)
                else:
                    new_rel_object = CloneMixin._create_copy_of_instance(
                        rel_object, force=True
                    )
                    new_rel_object.save()
                setattr(duplicate, field.name, new_rel_object)

        return duplicate

    def __duplicate_o2m_m2o_fields(self, duplicate):
        """
        Duplicate many to one or one to many fields.

        :param duplicate: The transient instance that should be duplicated.
        :type duplicate: `django.db.models.Model`
        :return: The duplicate instance with all the many to one or one to many fields duplicated.
        """
        fields = set()

        if self._clone_m2o_or_o2m_fields or self._clone_excluded_m2o_or_o2m_fields:
            for f in self._meta.related_objects:
                if any(
                    [
                        any([f.many_to_one, f.one_to_many])
                        and f.name in self._clone_m2o_or_o2m_fields,
                        any([f.many_to_one, f.one_to_many])
                        and f.name not in self._clone_excluded_m2o_or_o2m_fields,
                    ]
                ):
                    fields.add(f)

        # Clone one to many/many to one fields
        for field in fields:
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

        return duplicate

    def __duplicate_m2m_fields(self, duplicate, sub_clone):
        """
        Duplicate many to many fields.

        :param duplicate: The transient instance that should be duplicated.
        :type duplicate: `django.db.models.Model`
        :param sub_clone: Boolean indicating that the instance is a sub instance
            i.e a related field of a top level instance.
        :return: The duplicate instance with all the many to many fields duplicated.
        """
        fields = set()

        # Duplicating sub instance many to many fields not currently supported.
        if sub_clone:
            return duplicate

        if self._clone_m2m_fields or self._clone_excluded_m2m_fields:
            for f in chain(self._meta.related_objects, self._meta.many_to_many):
                if any(
                    [
                        f.many_to_many and f.name in self._clone_m2m_fields,
                        f.many_to_many
                        and f.name not in self._clone_excluded_m2m_fields,
                    ]
                ):
                    fields.add(f)

        # Clone many to many fields
        for field in fields:
            if hasattr(field, "field"):
                # ManyToManyRel
                field_name = field.field.m2m_reverse_field_name()
                through = field.through
                source = getattr(self, field.related_name)
                destination = getattr(duplicate, field.related_name)
            else:
                through = field.remote_field.through
                field_name = field.m2m_field_name()
                source = getattr(self, field.attname)
                destination = getattr(duplicate, field.attname)
            if all(
                [
                    through,
                    not through._meta.auto_created,
                ]
            ):
                objs = through.objects.filter(**{field_name: self.pk})
                for item in objs:
                    if hasattr(through, "make_clone"):
                        item.make_clone(attrs={field_name: duplicate}, sub_clone=True)
                    else:
                        item.pk = None
                        setattr(item, field_name, duplicate)
                        item.save()
            else:
                destination.set(source.all())

        return duplicate

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

        duplicate = self.__duplicate_o2o_fields(duplicate)
        duplicate.full_clean()
        duplicate.save()

        duplicate = self.__duplicate_o2m_m2o_fields(duplicate)
        duplicate = self.__duplicate_m2m_fields(duplicate, sub_clone)
        return duplicate

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
                        "An Unknown error has occurred: Expected ({}) >= ({})".format(
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
