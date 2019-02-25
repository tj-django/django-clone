## django-clone

A django library for creating clones (i.e a copy) of a model instance on the fly. 


```python
from model_clone import CloneMixin
from django.db import models

class TestModel(CloneMixin, models.Model):
    field_1 = models.CharField(max_length=200)
    rel_field =  models.ManyToManyField(Rel)

    _clonable_many_to_many_fields = ['rel_field']
```


Creating a clone

```python

In [2]: test_obj = TestModel.objects.first()

In [3]: clone = test_obj.make_clone(attrs={'field_1': 'Updated'})

In [4]: test_obj.field_1
Out[4]: 'Default'

In [5]: clone.field_1
Out[5]: 'Updated'
```
