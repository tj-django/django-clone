##django-clone

A django library for creating clone (i.e a copy) of a model instance on the fly. 


```python
_clonable_many_to_many_fields = ['tags', 'audiences']
_clonable_many_to_one_or_one_to_one_fields = ['treatments', 'attributes']
_clonable_one_to_one_fields = ['preheader']
```


```python
from model_clone import CloneMixin
from django.db import models

class TestModel(CloneMixin, models.Model):
    field_1 = models.CharField(max_length=200)
    rel_field =  models.ManyToManyField(Rel)

    _clonable_many_to_many_fields = ['tags', 'audiences']
    _clonable_many_to_one_fields = ['treatments', 'attributes']
```
