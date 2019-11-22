[![CircleCI](https://circleci.com/gh/jackton1/django-clone.svg?style=shield)](https://circleci.com/gh/jackton1/django-clone)
[![All Contributors](https://img.shields.io/badge/all_contributors-3-orange.svg?style=flat-square)](#contributors)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/django_clone.svg)](https://pypi.org/project/django-clone)
[![PyPI - License](https://img.shields.io/pypi/l/django_clone.svg)](https://github.com/jackton1/django-clone/blob/master/LICENSE)
[![PyPI - Django Version](https://img.shields.io/pypi/djversions/django_clone.svg)](https://docs.djangoproject.com/en/2.2/releases/)
## django-clone 

Creating copies of a model instance on the fly offering more control on how the object should be cloned with support for limiting fields or related objects copied with unique field detection. 

## Table of contents
* [Installation](#Installation)  
* [Usage](#Usage)
    * [Duplicate a Model Instance](#duplicating-a-model-instance)
    * [CloneMixin attributes](#clonemixin-attributes)
    * [Creating clones without subclassing `CloneMixin`](#creating-clones-without-subclassing-clonemixin)
* [Duplicating Models from Django Admin view](#duplicating-models-from-django-admin-view)


### Installation

```bash
pip install django-clone
```

Add `model_clone` to your INSTALLED_APPS

```python
INSTALLED_APPS = [
    ...
    'model_clone',
    ...
]
```


### Usage

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


#### Duplicating a model instance

```python
In [1]: test_obj = TestModel.objects.create(title='New')

In [2]: test_obj.tags.create(name='men')

In [3]: test_obj.tags.create(name='women')

In [4]: clone = test_obj.make_clone(attrs={'title': 'Updated title'})

In [5]: test_obj.pk
Out[5]: 1

In [6]: test_obj.title
Out[6]: 'New'

In [7]: test_obj.tags.all()
Out[7]: <QuerySet [<Tag: men>, <Tag: women>]>

In [8]: clone.pk
Out[8]: 2

In [9]: clone.title
Out[9]: 'Updated title'

In [10]: clone.tags.all()
Out[10]: <QuerySet [<Tag: men>, <Tag: women>]>
```

#### CloneMixin attributes

```text
_clonable_model_fields: Restrict the list of fields to copy from the instance.
_clonable_many_to_many_fields: Restricted Many to many fields (i.e Test.tags).
_clonable_many_to_one_or_one_to_many_fields: Restricted Many to One/One to Many fields.
_clonable_one_to_one_fields: Restricted One to One fields.
```

#### Creating clones without subclassing `CloneMixin`.

> :warning: This method won't copy over related objects like Many to Many/One to Many relationships.

> :warning: Ensure that required fields skipped from being cloned are passed in using the `attrs` dictionary.

```python

In [1]: from model_clone import create_copy_of_instance

In [2]: test_obj = TestModel.objects.create(title='New')

In [3]: test_obj.tags.create(name='men')

In [4]: test_obj.tags.create(name='women')

In [5]: clone = create_copy_of_instance(test_obj, attrs={'title': 'Updated title'})

In [6]: test_obj.pk
Out[6]: 1

In [7]: test_obj.title
Out[7]: 'New'

In [8]: test_obj.tags.all()
Out[8]: <QuerySet [<Tag: men>, <Tag: women>]>

In [9]: clone.pk
Out[9]: 2

In [10]: clone.title
Out[10]: 'Updated title'

In [11]: clone.tags.all()
Out[11]: <QuerySet []>
```


### Duplicating Models from Django Admin view.

Change
 
```python
from django.contrib import admin
from django.contrib.admin import ModelAdmin

@admin.register(TestModel)
class ModelToCloneAdmin(ModelAdmin):
    pass
```

to

```python
from model_clone import ClonableModelAdmin

@admin.register(TestModel)
class ModelToCloneAdmin(ClonableModelAdmin):
    pass
```

#### List View
![Screenshot](Duplicate-action.png)

#### Change View
![Screenshot](Duplicate-button.png)


##### SETTINGS
`include_duplicate_action`: Enables/Disables the Duplicate action in the List view (Defaults to True)
`include_duplicate_object_link`: Enables/Disables the Duplicate action in the Change view (Defaults to 
True)


> :warning: Ensure that `model_clone` is placed before `django.contrib.admin`

```python
INSTALLED_APPS = [
    'model_clone',
    'django.contrib.admin',
    '...',
]
```

## Contributors ✨

Thanks goes to these wonderful people:

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore -->
<table>
  <tr>
    <td align="center"><a href="http://gerritneven.nl"><img src="https://avatars1.githubusercontent.com/u/2500973?v=4" width="100px;" alt="Gerben Neven"/><br /><sub><b>Gerben Neven</b></sub></a><br /><a href="https://github.com/jackton1/django-clone/issues?q=author%3Agerbyzation" title="Bug reports">🐛</a> <a href="https://github.com/jackton1/django-clone/commits?author=gerbyzation" title="Tests">⚠️</a> <a href="https://github.com/jackton1/django-clone/commits?author=gerbyzation" title="Code">💻</a></td>
    <td align="center"><a href="http://sebastian-kindt.com"><img src="https://avatars1.githubusercontent.com/u/2536081?v=4" width="100px;" alt="Sebastian Kapunkt"/><br /><sub><b>Sebastian Kapunkt</b></sub></a><br /><a href="https://github.com/jackton1/django-clone/commits?author=SebastianKapunkt" title="Code">💻</a> <a href="https://github.com/jackton1/django-clone/issues?q=author%3ASebastianKapunkt" title="Bug reports">🐛</a></td>
    <td align="center"><a href="https://github.com/andresp99999"><img src="https://avatars0.githubusercontent.com/u/1036725?v=4" width="100px;" alt="Andrés Portillo"/><br /><sub><b>Andrés Portillo</b></sub></a><br /><a href="https://github.com/jackton1/django-clone/issues?q=author%3Aandresp99999" title="Bug reports">🐛</a></td>
  </tr>
</table>

<!-- ALL-CONTRIBUTORS-LIST:END -->

This project follows the [all-contributors](https://github.com/all-contributors/all-contributors) specification. Contributions of any kind welcome!
