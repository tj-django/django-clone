import abc

from django.core.exceptions import ValidationError
from django.db import transaction, models
from django.db.models import SlugField
from django.db.models.base import ModelBase
from django.utils import six
from django.utils.text import slugify


class CloneMetaClass(abc.ABCMeta, ModelBase):
    pass


class CloneMixin(six.with_metaclass(CloneMetaClass)):
    """
    CloneMixin mixin to duplicate an object using the model cls.

    Examples:
        class TestModel(CloneMixin, models.Model):
            field_1 = models.CharField(max_length=200)
            rel_field =  models.ManyToManyField(Rel)

            _clonable_many_to_many_fields = ['tags', 'audiences']
            _clonable_many_to_one_fields = ['treatments', 'attributes']
            ...

    Attributes:
        _clonable_model_fields: Restricted list of fields to copy from the instance.
        _clonable_many_to_many_fields (list): Many to many fields (i.e Event.tags).
        _clonable_many_to_one_or_one_to_many_fields (list): Many to one/One to many fields (Event.eventtreatment).
        _clonable_one_to_one_fields (list): One to One fields (Event.preheader)
    """
    _clonable_model_fields = []
    _clonable_many_to_many_fields = []
    _clonable_many_to_one_or_one_to_many_fields = []
    _clonable_one_to_one_fields = []

    UNIQUE_DUPLICATE_SUFFIX = 'copy'
    USE_UNIQUE_DUPLICATE_SUFFIX = True

    @property
    @abc.abstractmethod
    def objects(self):
        pass

    @classmethod
    def _create_copy_of_instance(cls, instance):
        defaults = {}
        fields = [f for f in instance._meta.concrete_fields if not f.primary_key]

        if cls._clonable_model_fields:
            fields = [f for f in fields if f.name in cls._clonable_model_fields]

        unique_field_names = cls.unpack_unique_together(
            opts=instance._meta,
            only_fields=[f.attname for f in fields],
        )

        unique_fields = [
            f.name for f in fields if not f.auto_created and (f.unique or f.name in unique_field_names)
        ]

        for f in fields:
            if all([
                not f.auto_created,
                f.concrete,
                f.editable,
                f not in instance._meta.related_objects,
                f not in instance._meta.many_to_many,
            ]):
                value = getattr(instance, f.attname, f.get_default())
                if f.attname in unique_fields and isinstance(f, models.CharField):
                    count = (
                        instance.__class__._default_manager
                        .filter(**{'{}__startswith'.format(f.attname): value})
                        .count()
                    )
                    if cls.USE_UNIQUE_DUPLICATE_SUFFIX:
                        if not str(value).isdigit():
                            value += ' {} {}'.format(cls.UNIQUE_DUPLICATE_SUFFIX, count)
                    if isinstance(f, SlugField):
                        value = slugify(value)
                defaults[f.attname] = value

        return cls(**defaults)

    @transaction.atomic
    def make_clone(self, attrs=(), sub_clone=False):
        """
        Creates a clone of the django model instance.

        :param attrs (dict): Dictionary of attributes to be replaced on the cloned object.
        :param sub_clone (bool): Internal boolean used to detect cloning sub objects.
        :rtype: :obj:`django.db.models.Model`
        :return: The model instance that has been cloned.
        """
        attrs = attrs or {}
        if not self.pk:
            raise ValidationError('{}: Instance must be saved before it can be cloned.'.format(self.__class__.__name__))
        if sub_clone:
            duplicate = self
            duplicate.pk = None
        else:
            duplicate = self._create_copy_of_instance(self)
            # Supports only updating the attributes of the base instance.
            for name, value in attrs.items():
                setattr(duplicate, name, value)

        duplicate.save()

        one_to_one_fields = [
            f for f in self._meta.related_objects
            if f.one_to_one and f.name in self._clonable_one_to_one_fields
        ]

        many_to_one_or_one_to_many_fields = [
            f for f in self._meta.related_objects
            if any([f.many_to_one, f.one_to_many])
            and f.name in self._clonable_many_to_one_or_one_to_many_fields
        ]

        many_to_many_fields = [
            f for f in self._meta.many_to_many
            if not sub_clone and f.name in self._clonable_many_to_many_fields
        ]

        # Clone one to one fields
        for field in one_to_one_fields:
            rel_object = getattr(self, field.related_name, None)
            if rel_object:
                if hasattr(rel_object, 'make_clone'):
                    rel_object.make_clone(attrs={field.remote_field.name: duplicate}, sub_clone=True)
                else:
                    rel_object.pk = None
                    setattr(rel_object, field.remote_field.name, duplicate)
                    rel_object.save()

        # Clone one to many/many to one fields
        for field in many_to_one_or_one_to_many_fields:
            getattr(duplicate, field.related_name).set(getattr(self, field.related_name).all())

        # Clone many to many fields
        for field in many_to_many_fields:
            if field.remote_field.through and not field.remote_field.through._meta.auto_created:
                objs = field.remote_field.through.objects.filter(**{field.m2m_field_name(): self.pk})
                for item in objs:
                    if hasattr(field.remote_field.through, 'make_clone'):
                        item.make_clone(attrs={field.m2m_field_name(): duplicate}, sub_clone=True)
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
