import itertools
from itertools import repeat
from typing import Dict, List, Optional

from conditional import conditional
from django.core.checks import Error
from django.core.exceptions import ValidationError
from django.db import IntegrityError, connections, models, transaction
from django.db.models import SlugField
from django.utils.text import slugify

from model_clone.apps import ModelCloneConfig
from model_clone.utils import (
    clean_value,
    context_mutable_attribute,
    get_fields_and_unique_fields_from_cls,
    get_unique_default,
    get_unique_value,
    get_value,
    transaction_autocommit,
)


class CloneMixin(object):

    """CloneMixin mixin to duplicate an object using the model's class.

    :param _clone_fields: Restricted List of fields to copy from the instance.
    :type _clone_fields: collections.Iterable
    :param _clone_m2m_fields: Many to many fields (Example: TestModel.tags).
    :type _clone_m2m_fields: collections.Iterable
    :param _clone_m2o_or_o2m_fields: Many to one/One to many fields.
    :type _clone_m2o_or_o2m_fields: collections.Iterable
    :param _clone_o2o_fields: One to One fields.
    :type _clone_o2o_fields: collections.Iterable

    :param _clone_excluded_fields: Excluded model fields.
    :type _clone_excluded_fields: collections.Iterable
    :param _clone_excluded_m2m_fields: Excluded many to many fields.
    :type _clone_excluded_m2m_fields: collections.Iterable
    :param _clone_excluded_m2o_or_o2m_fields: Excluded many to many
        and one to many fields.
    :type _clone_excluded_m2o_or_o2m_fields: collections.Iterable
    :param _clone_excluded_o2o_fields: Excluded one to one fields.
    :type _clone_excluded_o2o_fields: collections.Iterable

    :Example:
    >>> from django.conf import settings
    >>> from django.db import models
    >>>
    >>> # Using explicit fields
    >>>
    >>> class TestModel1(CloneMixin, models.Model):
    >>>     field_1 = models.CharField(max_length=200)
    >>>     tags =  models.ManyToManyField(Tags)
    >>>     audiences = models.ManyToManyField(Audience)
    >>>     user = models.ForiegnKey(
    >>>         settings.AUTH_USER_MODEL,
    >>>         on_delete=models.CASCADE,
    >>>     )
    >>>
    >>>     _clone_m2m_fields = ['tags', 'audiences']
    >>>     _clone_m2o_or_o2m_fields = ['user']
    >>>     ...
    >>>
    >>> # Using implicit all except fields.
    >>>
    >>> class TestModel2(CloneMixin, models.Model):
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

    DUPLICATE_SUFFIX = "copy"  # type: str
    USE_DUPLICATE_SUFFIX_FOR_NON_UNIQUE_FIELDS = False  # type: bool
    UNIQUE_DUPLICATE_SUFFIX = "copy"  # type: str
    USE_UNIQUE_DUPLICATE_SUFFIX = True  # type: bool
    MAX_UNIQUE_DUPLICATE_QUERY_ATTEMPTS = 100  # type: int

    @classmethod
    def check(cls, **kwargs):  # pragma: no cover
        errors = super(CloneMixin, cls).check(**kwargs)

        if cls.USE_UNIQUE_DUPLICATE_SUFFIX and not cls.UNIQUE_DUPLICATE_SUFFIX:
            errors.append(
                Error(
                    "UNIQUE_DUPLICATE_SUFFIX is required.",
                    hint=(
                        "Please provide UNIQUE_DUPLICATE_SUFFIX"
                        f" for {cls.__name__} or set USE_UNIQUE_DUPLICATE_SUFFIX=False"
                    ),
                    obj=cls,
                    id=f"{ModelCloneConfig.name}.E001",
                )
            )

        if cls.USE_DUPLICATE_SUFFIX_FOR_NON_UNIQUE_FIELDS and not cls.DUPLICATE_SUFFIX:
            errors.append(
                Error(
                    "UNIQUE_DUPLICATE_SUFFIX is required.",
                    hint=(
                        f"Please provide DUPLICATE_SUFFIX for {cls.__name__} "
                        "or set USE_DUPLICATE_SUFFIX_FOR_NON_UNIQUE_FIELDS=False"
                    ),
                    obj=cls,
                    id=f"{ModelCloneConfig.name}.E001",
                )
            )

        if all([cls._clone_fields, cls._clone_excluded_fields]):
            errors.append(
                Error(
                    "Conflicting configuration.",
                    hint=(
                        'Please provide either "_clone_fields"'
                        f' or "_clone_excluded_fields" for model {cls.__name__}'
                    ),
                    obj=cls,
                    id=f"{ModelCloneConfig.name}.E002",
                )
            )

        if all([cls._clone_m2m_fields, cls._clone_excluded_m2m_fields]):
            errors.append(
                Error(
                    "Conflicting configuration.",
                    hint=(
                        'Please provide either "_clone_m2m_fields"'
                        f' or "_clone_excluded_m2m_fields" for model {cls.__name__}'
                    ),
                    obj=cls,
                    id=f"{ModelCloneConfig.name}.E002",
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
                        'Please provide either "_clone_m2o_or_o2m_fields" or '
                        f'"_clone_excluded_m2o_or_o2m_fields" for model {cls.__name__}'
                    ),
                    obj=cls,
                    id=f"{ModelCloneConfig.name}.E002",
                )
            )

        if all([cls._clone_o2o_fields, cls._clone_excluded_o2o_fields]):
            errors.append(
                Error(
                    "Conflicting configuration.",
                    hint=(
                        'Please provide either "_clone_o2o_fields" or '
                        f'"_clone_excluded_o2o_fields" for model {cls.__name__}'
                    ),
                    obj=cls,
                    id=f"{ModelCloneConfig.name}.E002",
                )
            )

        return errors

    @classmethod
    def bulk_clone_multi(cls, objs, attrs=None, batch_size=None):
        # type: (List[models.Model], Optional[List[Dict]], Optional[int]) -> List[models.Model]
        # TODO: Support bulk clones split by the batch_size
        pass

    def pre_save_duplicate(self, instance):  # pylint: disable=R0201
        """Override this method to modify the duplicate instance before it's saved."""
        return instance

    @transaction.atomic
    def make_clone(self, attrs=None, sub_clone=False, using=None):
        """Creates a clone of the django model instance.

        :param attrs: Dictionary of attributes to be replaced on the cloned object.
        :type attrs: dict
        :param sub_clone: Internal boolean used to detect cloning sub objects.
        :type sub_clone: bool
        :rtype: :obj:`django.db.models.Model`
        :param using: The database alias used to save the created instances.
        :type using: str
        :return: The model instance that has been cloned.
        """
        using = using or self._state.db or self.__class__._default_manager.db
        attrs = attrs or {}
        if not self.pk:
            raise ValidationError(
                "{}: Instance must be saved before it can be cloned.".format(
                    self.__class__.__name__
                )
            )
        if sub_clone:
            duplicate = self  # pragma: no cover
            duplicate.pk = None  # pragma: no cover
        else:
            duplicate = self._create_copy_of_instance(self, using=using)

        for name, value in attrs.items():
            setattr(duplicate, name, value)

        duplicate = self.pre_save_duplicate(duplicate)
        duplicate.save(using=using)

        duplicate = self.__duplicate_m2o_fields(duplicate, using=using)
        duplicate = self.__duplicate_o2o_fields(duplicate, using=using)
        duplicate = self.__duplicate_o2m_fields(duplicate, using=using)
        duplicate = self.__duplicate_m2m_fields(duplicate, using=using)

        return duplicate

    def bulk_clone(
        self, count, attrs=None, batch_size=None, using=None, auto_commit=False
    ):
        using = using or self._state.db or self.__class__._default_manager.db
        ops = connections[using].ops
        objs = range(count)
        clones = []
        batch_size = batch_size or max(ops.bulk_batch_size([], list(objs)), 1)

        with conditional(
            auto_commit,
            transaction_autocommit(using=using),
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
        # t^n i.e 100 ** 2ms = 10000ms (10s) to clone 100 objects.
        # I'll like to reduce this down to max time to clone count/batch_size i.e
        # If it take 10000ms to clone 100 objects with a db of batch_size 100
        # If it takes 20ms to clone 10 objects I'll like to keep this down to 20ms
        # i.e max_num_of_threads 10 for 100 objects.
        # This should run in parallel
        # Testing jit and cpython if they offer better API's.
        pass

    @staticmethod
    def _create_copy_of_instance(instance, using=None, force=False, sub_clone=False):
        """Create a copy of a model instance.

        :param instance: The instance to be duplicated.
        :type instance: `django.db.models.Model`
        :param using: The database alias used to save the created instances.
        :type using: str
        :param force: Flag to skip using the current model clone declared attributes.
        :type force: bool
        :param sub_clone: Flag to skip cloning one to one fields for sub clones.
        :type sub_clone: bool
        :return: A new transient instance.
        :rtype: `django.db.models.Model`
        """
        cls = instance.__class__
        clone_fields = getattr(cls, "_clone_fields", CloneMixin._clone_fields)
        clone_excluded_fields = getattr(
            cls, "_clone_excluded_fields", CloneMixin._clone_excluded_fields
        )
        clone_o2o_fields = getattr(
            cls, "_clone_o2o_fields", CloneMixin._clone_o2o_fields
        )
        clone_excluded_o2o_fields = getattr(
            cls, "_clone_excluded_o2o_fields", CloneMixin._clone_excluded_o2o_fields
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
        duplicate_suffix = getattr(
            cls,
            "DUPLICATE_SUFFIX",
            CloneMixin.DUPLICATE_SUFFIX,
        )
        use_duplicate_suffix_for_non_unique_fields = getattr(
            cls,
            "USE_DUPLICATE_SUFFIX_FOR_NON_UNIQUE_FIELDS",
            CloneMixin.USE_DUPLICATE_SUFFIX_FOR_NON_UNIQUE_FIELDS,
        )

        fields, unique_fields = get_fields_and_unique_fields_from_cls(
            model=cls,
            force=force,
            clone_fields=clone_fields,
            clone_excluded_fields=clone_excluded_fields,
            clone_o2o_fields=clone_o2o_fields,
            clone_excluded_o2o_fields=clone_excluded_o2o_fields,
        )

        new_instance = cls()

        for f in fields:
            if not f.editable:
                f.pre_save(new_instance, add=True)
                continue

            value = getattr(instance, f.attname)

            if all(
                [
                    not f.auto_created,
                    f.concrete,
                    f.editable,
                    f.name in unique_fields,
                ]
            ):
                # Do not try to get unique value for enum type field
                if all(
                    [
                        isinstance(f, (models.CharField, models.TextField)),
                        not f.choices,
                        isinstance(value, str),
                    ]
                ):
                    value = clean_value(value, unique_duplicate_suffix)

                    if f.has_default():
                        value = f.get_default()

                        if not callable(f.default) and isinstance(value, str):
                            value = get_unique_default(
                                model=cls,
                                fname=f.attname,
                                value=value,
                                transform=(
                                    slugify if isinstance(f, SlugField) else str
                                ),
                                suffix=unique_duplicate_suffix,
                                max_length=f.max_length,
                                max_attempts=max_unique_duplicate_query_attempts,
                            )

                    elif use_unique_duplicate_suffix and isinstance(value, str):
                        value = get_unique_value(
                            model=cls,
                            fname=f.attname,
                            value=value,
                            transform=(slugify if isinstance(f, SlugField) else str),
                            suffix=unique_duplicate_suffix,
                            max_length=f.max_length,
                            max_attempts=max_unique_duplicate_query_attempts,
                        )

                elif isinstance(f, models.OneToOneField) and not sub_clone:
                    sub_instance = getattr(instance, f.name, None) or f.get_default()

                    if sub_instance is not None:
                        sub_instance = CloneMixin._create_copy_of_instance(
                            sub_instance,
                            force=True,
                            sub_clone=True,
                        )
                        sub_instance.save(using=using)
                        value = sub_instance.pk
            elif all(
                [
                    use_duplicate_suffix_for_non_unique_fields,
                    f.concrete,
                    f.editable,
                    f.name not in unique_fields,
                ]
            ):
                if (
                    isinstance(f, (models.CharField, models.TextField))
                    and not f.choices
                ):
                    value = get_value(
                        value=value,
                        transform=(slugify if isinstance(f, SlugField) else str),
                        suffix=duplicate_suffix,
                        max_length=f.max_length,
                    )

            setattr(new_instance, f.attname, value)

        return new_instance

    def __duplicate_o2o_fields(self, duplicate, using=None):
        """Duplicate one to one fields.
        :param duplicate: The transient instance that should be duplicated.
        :type duplicate: `django.db.models.Model`
        :param using: The database alias used to save the created instances.
        :type using: str
        :return: The duplicate instance with all the one to one fields duplicated.
        """
        for f in self._meta.related_objects:
            if f.one_to_one:
                if any(
                    [
                        f.name in self._clone_o2o_fields
                        and f not in self._meta.concrete_fields,
                        self._clone_excluded_o2o_fields
                        and f.name not in self._clone_excluded_o2o_fields
                        and f not in self._meta.concrete_fields,
                    ]
                ):
                    rel_object = getattr(self, f.name, None)
                    if rel_object:
                        new_rel_object = CloneMixin._create_copy_of_instance(
                            rel_object,
                            force=True,
                            sub_clone=True,
                        )
                        setattr(new_rel_object, f.remote_field.name, duplicate)
                        new_rel_object.save(using=using)

        return duplicate

    def __duplicate_o2m_fields(self, duplicate, using=None):
        """Duplicate one to many fields.

        :param duplicate: The transient instance that should be duplicated.
        :type duplicate: `django.db.models.Model`
        :param using: The database alias used to save the created instances.
        :type using: str
        :return: The duplicate instance with all the transient one to many duplicated instances.
        """

        for f in itertools.chain(
            self._meta.related_objects, self._meta.concrete_fields
        ):
            if f.one_to_many:
                if any(
                    [
                        f.get_accessor_name() in self._clone_m2o_or_o2m_fields,
                        self._clone_excluded_m2o_or_o2m_fields
                        and f.get_accessor_name()
                        not in self._clone_excluded_m2o_or_o2m_fields,
                    ]
                ):
                    for item in getattr(self, f.get_accessor_name()).all():
                        if hasattr(item, "make_clone"):
                            try:
                                item.make_clone(
                                    attrs={f.remote_field.name: duplicate},
                                    using=using,
                                )
                            except IntegrityError:
                                item.make_clone(
                                    attrs={f.remote_field.name: duplicate},
                                    save_new=False,
                                    sub_clone=True,
                                    using=using,
                                )
                        else:
                            new_item = CloneMixin._create_copy_of_instance(
                                item,
                                force=True,
                                sub_clone=True,
                                using=using,
                            )
                            setattr(new_item, f.remote_field.name, duplicate)

                            new_item.save(using=using)

        return duplicate

    def __duplicate_m2o_fields(self, duplicate, using=None):
        """Duplicate many to one fields.

        :param duplicate: The transient instance that should be duplicated.
        :type duplicate: `django.db.models.Model`
        :param using: The database alias used to save the created instances.
        :type using: str
        :return: The duplicate instance with all the many to one fields duplicated.
        """
        for f in self._meta.concrete_fields:
            if f.many_to_one:
                if any(
                    [
                        f.name in self._clone_m2o_or_o2m_fields,
                        self._clone_excluded_m2o_or_o2m_fields
                        and f.name not in self._clone_excluded_m2o_or_o2m_fields,
                    ]
                ):
                    item = getattr(self, f.name)
                    if hasattr(item, "make_clone"):
                        try:
                            item_clone = item.make_clone(using=using)
                        except IntegrityError:
                            item_clone = item.make_clone(sub_clone=True)
                    else:
                        item.pk = None  # pragma: no cover
                        item_clone = item.save(using=using)  # pragma: no cover

                    setattr(duplicate, f.name, item_clone)

        return duplicate

    def __duplicate_m2m_fields(self, duplicate, using=None):
        """Duplicate many to many fields.

        :param duplicate: The transient instance that should be duplicated.
        :type duplicate: `django.db.models.Model`
        :param using: The database alias used to save the created instances.
        :type using: str
        :return: The duplicate instance with all the many to many fields duplicated.
        """
        fields = set()

        for f in self._meta.many_to_many:
            if any(
                [
                    f.name in self._clone_m2m_fields,
                    self._clone_excluded_m2m_fields
                    and f.name not in self._clone_excluded_m2m_fields,
                ]
            ):
                fields.add(f)

        for f in self._meta.related_objects:
            if f.many_to_many:
                if any(
                    [
                        f.get_accessor_name() in self._clone_m2m_fields,
                        self._clone_excluded_m2m_fields
                        and f.get_accessor_name()
                        not in self._clone_excluded_m2m_fields,
                    ]
                ):
                    fields.add(f)

        # Clone many to many fields
        for field in fields:
            if hasattr(field, "field"):
                # ManyToManyRel
                field_name = field.field.m2m_reverse_field_name()
                through = field.through
                source = getattr(self, field.get_accessor_name())
                destination = getattr(duplicate, field.get_accessor_name())
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
                        try:
                            item.make_clone(
                                attrs={field_name: duplicate},
                                using=using,
                            )
                        except IntegrityError:
                            item.make_clone(
                                attrs={field_name: duplicate},
                                sub_clone=True,
                                using=using,
                            )
                    else:
                        item.pk = None
                        setattr(item, field_name, duplicate)
                        item.save(using=using)
            else:
                destination.set(source.all())

        return duplicate
