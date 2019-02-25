import abc

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models.base import ModelBase
from django.utils import six


@six.with_metaclass(abc.ABCMeta, ModelBase)
class CloneMixin(object):
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

    @property
    @abc.abstractmethod
    def _meta(self):
        pass

    @property
    @abc.abstractmethod
    def objects(self):
        pass

    @classmethod
    def _create_copy_of_instance(cls, instance):
        defaults = {}
        fields = instance._meta.concrete_fields
        if cls._clonable_model_fields:
            fields = [f for f in fields if f.name in cls._clonable_model_fields]

        for f in fields:
            if all([
                not f.auto_created,
                f.concrete,
                f.editable,
                f not in instance._meta.related_objects,
                f not in instance._meta.many_to_many,
            ]):
                defaults[f.attname] = getattr(instance, f.attname, f.get_default())

        return cls.objects.create(**defaults)

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
            raise ValidationError(f'{self.__class__.__name__}: Instance must be saved before it can be cloned.')
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
            f.name for f in self._meta.related_objects
            if any([f.many_to_one, f.one_to_many, f.one_to_one])
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
