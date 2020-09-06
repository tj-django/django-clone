|    PyPI                        |  Python   | Django  | [LICENSE](./LICENSE) |
|:------------------------------:|:---------:|:-------:|:--------------------:|
| [![PyPI version](https://badge.fury.io/py/django-clone.svg)](https://badge.fury.io/py/django-clone) | [![PyPI - Python Version](https://img.shields.io/pypi/pyversions/django_clone.svg)](https://pypi.org/project/django-clone) | [![PyPI - Django Version](https://img.shields.io/pypi/djversions/django_clone.svg)](https://docs.djangoproject.com/en/3.0/releases/) | [![PyPI - License](https://img.shields.io/pypi/l/django_clone.svg)](https://github.com/jackton1/django-clone/blob/master/LICENSE)


| Test | Vulnerabilities | Coverage | Code Quality  | Contributors  | 
|:----:|:---------------:|:--------:|:-------------:|:-------------:|
| [![CircleCI](https://circleci.com/gh/tj-django/django-clone.svg?style=shield)](https://circleci.com/gh/tj-django/django-clone) | [![Known Vulnerabilities](https://snyk.io/test/github/tj-django/django-clone/badge.svg?targetFile=requirements.txt)](https://snyk.io/test/github/tj-django/django-clone?targetFile=requirements.txt) | [![Codacy Badge](https://app.codacy.com/project/badge/Coverage/b33dd02dbb034d7fa9886a99f5383ea6)](https://www.codacy.com/gh/tj-django/django-clone?utm_source=github.com&utm_medium=referral&utm_content=tj-django/django-clone&utm_campaign=Badge_Coverage) | [![Codacy Badge](https://app.codacy.com/project/badge/Grade/b33dd02dbb034d7fa9886a99f5383ea6)](https://www.codacy.com/gh/tj-django/django-clone?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=tj-django/django-clone&amp;utm_campaign=Badge_Grade) | [![All Contributors](https://img.shields.io/badge/all_contributors-5-orange.svg?style=flat-square)](#contributors)





## django-clone 

Creating copies of a model instance with explicit control on how the instance should be duplicated (limiting fields or related objects) copied and unique field detection. 

## Table of contents

-   [Installation](#Installation)

-   [Usage](#Usage)
    -   [Duplicate a Model Instance](#duplicating-a-model-instance)
    -   [Using the CloneMixin](#clonemixin-attributes)
    -   [Creating clones without subclassing `CloneMixin`](#creating-clones-without-subclassing-clonemixin)

-   [Duplicating Models from Django Admin view](#duplicating-models-from-django-admin-view)

-   [Change Log](./CHANGELOG.md)

### Installation

Run 
```bash script
$ pip install django-clone
```


### Usage

```python
from django.db import models
from django.utils.translation import gettext_lazy as _
from model_clone import CloneMixin

class TestModel(CloneMixin, models.Model):
    title = models.CharField(max_length=200)
    tags =  models.ManyToManyField('Tags')

    _clone_many_to_many_fields = ['tags']
    

class Tags(models.Model):
    name = models.CharField(max_length=255)
    
    def __str__(self):
        return _(self.name)
```

#### Duplicating a model instance

```python
In [1]: test_obj = TestModel.objects.create(title='New')

In [2]: test_obj.pk
Out[2]: 1

In [3]: test_obj.title
Out[3]: 'New'

In [4]: test_obj.tags.create(name='men')

In [4]: test_obj.tags.create(name='women')

In [5]: test_obj.tags.all()
Out[5]: <QuerySet [<Tag: men>, <Tag: women>]>

In [6]: clone = test_obj.make_clone(attrs={'title': 'Updated title'})

In [7]: clone.pk
Out[7]: 2

In [8]: clone.title
Out[8]: 'Updated title'

In [9]: clone.tags.all()
Out[9]: <QuerySet [<Tag: men>, <Tag: women>]>
```

#### CloneMixin attributes

##### Explicit

|    Field Names        |  Description |
|:------------------------------:|:------------:|
| `_clone_model_fields` | Restrict the list of fields to copy from the instance (By default: Copies all fields excluding auto-created/non editable model fields) |
`_clone_many_to_many_fields` | Restricted Many to many fields (i.e Test.tags) |
`_clone_many_to_one_or_one_to_many_fields` | Restricted Many to One/One to Many fields | 
`_clone_one_to_one_fields` | Restricted One to One fields |

##### Implicit

|  Field Names (include all except these fields.) | Description |
|:--------------------:|:-----------:|
| `_clone_excluded_model_fields` | Excluded model fields. |
`_clone_excluded_many_to_many_fields` | Excluded many to many fields. |
`_clone_excluded_many_to_one_or_one_to_many_fields` |  Excluded Many to One/One to Many fields. |
`_clone_excluded_one_to_one_fields` | Excluded one to one fields. |


> :warning: NOTE: Ensure to either set `_clone_excluded_*` or `_clone_*`. Using both would raise errors. 

#### Creating clones without subclassing `CloneMixin`.

```python

In [1]: from model_clone import create_copy_of_instance

In [2]: test_obj = TestModel.objects.create(title='New')

In [3]: test_obj.pk
Out[3]: 1

In [4]: test_obj.title
Out[4]: 'New'

In [5]: test_obj.tags.create(name='men')

In [6]: test_obj.tags.create(name='women')

In [7]: test_obj.tags.all()
Out[7]: <QuerySet [<Tag: men>, <Tag: women>]>

In [8]: clone = create_copy_of_instance(test_obj, attrs={'title': 'Updated title'})

In [9]: clone.pk
Out[9]: 2

In [10]: clone.title
Out[10]: 'Updated title'

In [11]: clone.tags.all()
Out[11]: <QuerySet []>
```

> :warning: NOTE:
> - This method won't copy over related objects like Many to Many/One to Many relationships. 
> - Ensure that required fields skipped from being cloned are passed in using the `attrs` dictionary.

### Duplicating Models from Django Admin view.

Change

```python
from django.contrib import admin
from django.contrib.admin import ModelAdmin

@admin.register(TestModel)
class TestModelAdmin(ModelAdmin):
    pass
```

to

```python
from model_clone import CloneModelAdmin

@admin.register(TestModel)
class TestModelAdmin(CloneModelAdmin):
    pass
```

#### List View

![Screenshot](Duplicate-action.png)

#### Change View

![Screenshot](Duplicate-button.png)

##### CLONE MODEL ADMIN CLASS PROPERTIES

```python

from model_clone import CloneModelAdmin

@admin.register(TestModel)
class TestModelAdmin(CloneModelAdmin):
    # Enables/Disables the Duplicate action in the List view (Defaults to True)
    include_duplicate_action = True
    # Enables/Disables the Duplicate action in the Change view (Defaults to True)
    include_duplicate_object_link = True
```


> :warning: NOTE: Ensure that `model_clone` is placed before `django.contrib.admin`

```python
INSTALLED_APPS = [
    'model_clone',
    'django.contrib.admin',
    '...',
]
```

### Found a Bug?
To file a bug or submit a patch, please head over to [django-clone on github](https://github.com/jackton1/django-clone).


## Contributors ✨

Thanks goes to these wonderful people:

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->
<!-- prettier-ignore-start -->
<!-- markdownlint-disable -->
<table>
  <tr>
    <td align="center"><a href="http://gerritneven.nl"><img src="https://avatars1.githubusercontent.com/u/2500973?v=4" width="100px;" alt=""/><br /><sub><b>Gerben Neven</b></sub></a><br /><a href="https://github.com/tj-django/django-clone/issues?q=author%3Agerbyzation" title="Bug reports">🐛</a> <a href="https://github.com/tj-django/django-clone/commits?author=gerbyzation" title="Tests">⚠️</a> <a href="https://github.com/tj-django/django-clone/commits?author=gerbyzation" title="Code">💻</a></td>
    <td align="center"><a href="http://sebastian-kindt.com"><img src="https://avatars1.githubusercontent.com/u/2536081?v=4" width="100px;" alt=""/><br /><sub><b>Sebastian Kapunkt</b></sub></a><br /><a href="https://github.com/tj-django/django-clone/commits?author=SebastianKapunkt" title="Code">💻</a> <a href="https://github.com/tj-django/django-clone/issues?q=author%3ASebastianKapunkt" title="Bug reports">🐛</a> <a href="https://github.com/tj-django/django-clone/commits?author=SebastianKapunkt" title="Tests">⚠️</a></td>
    <td align="center"><a href="https://github.com/andresp99999"><img src="https://avatars0.githubusercontent.com/u/1036725?v=4" width="100px;" alt=""/><br /><sub><b>Andrés Portillo</b></sub></a><br /><a href="https://github.com/tj-django/django-clone/issues?q=author%3Aandresp99999" title="Bug reports">🐛</a></td>
    <td align="center"><a href="https://renovate.whitesourcesoftware.com"><img src="https://avatars0.githubusercontent.com/u/25180681?v=4" width="100px;" alt=""/><br /><sub><b>WhiteSource Renovate</b></sub></a><br /><a href="#maintenance-renovate-bot" title="Maintenance">🚧</a></td>
    <td align="center"><a href="https://github.com/yuekui"><img src="https://avatars2.githubusercontent.com/u/2561450?v=4" width="100px;" alt=""/><br /><sub><b>Yuekui</b></sub></a><br /><a href="https://github.com/tj-django/django-clone/commits?author=yuekui" title="Code">💻</a> <a href="https://github.com/tj-django/django-clone/issues?q=author%3Ayuekui" title="Bug reports">🐛</a> <a href="https://github.com/tj-django/django-clone/commits?author=yuekui" title="Tests">⚠️</a></td>
  </tr>
</table>

<!-- markdownlint-enable -->
<!-- prettier-ignore-end -->
<!-- ALL-CONTRIBUTORS-LIST:END -->

This project follows the [all-contributors](https://github.com/all-contributors/all-contributors) specification. Contributions of any kind welcome!
