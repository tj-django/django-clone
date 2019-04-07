[![CircleCI](https://circleci.com/gh/jackton1/django-clone.svg?style=shield)](https://circleci.com/gh/jackton1/django-clone)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/django_clone.svg)](https://pypi.org/project/django-clone)
![PyPI - License](https://img.shields.io/pypi/l/django_clone.svg)
[![PyPI - Django Version](https://img.shields.io/pypi/djversions/django_clone.svg)](https://docs.djangoproject.com/en/2.2/releases/)
## django-clone 

Creating clones (i.e a copy) of a model instance on the fly. 


```python
from django.db import models
from django.utils.translation import gettext_lazy as _
from model_clone import CloneMixin

class Tags(models.Model):
    name = models.CharField(max_length=255)
    
    def __str__(self):
        return _(self.name)


class TestModel(CloneMixin, models.Model):
    title = models.CharField(max_length=200)
    tags =  models.ManyToManyField(Tags)

    _clonable_many_to_many_fields = ['tags']
```


Creating a clone

```python
In [1]: test_obj = TestModel.objects.create(title='New')

In [2]: test_obj.tags.create(name='men')

In [3]: test_obj.tags.create(name='women')

In [4]: clone = test_obj.make_clone(attrs={'title': 'Updated title'})

In [5]: test_obj.title
Out[5]: 'New'

In [6]: test_obj.tags.all()
Out[6]: <QuerySet [<Tag: men>, <Tag: women>]>

In [7]: clone.title
Out[7]: 'Updated title'

In [8]: clone.tags.all()
Out[8]: <QuerySet [<Tag: men>, <Tag: women>]>
```
