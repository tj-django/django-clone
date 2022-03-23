|  Python   | Django  |  Downloads  |   Code Style   |
|:---------:|:-------:|:-----------:|:--------------:|
| [![PyPI - Python Version](https://img.shields.io/pypi/pyversions/django_clone.svg)](https://pypi.org/project/django-clone) | [![PyPI - Django Version](https://img.shields.io/pypi/djversions/django_clone.svg)](https://docs.djangoproject.com/en/3.2/releases/) | [![Downloads](https://pepy.tech/badge/django-clone)](https://pepy.tech/project/django-clone) | [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black) |

|    PyPI         | Test | Vulnerabilities | Coverage | Code Quality  | Dependencies   |  Pre-Commit   |
|:---------------:|:----:|:---------------:|:--------:|:-------------:|:--------------:|:-------------:|
| [![PyPI version](https://badge.fury.io/py/django-clone.svg)](https://badge.fury.io/py/django-clone) | [![Test](https://github.com/tj-django/django-clone/workflows/Test/badge.svg)](https://github.com/tj-django/django-clone/actions?query=workflow%3ATest) | [![Known Vulnerabilities](https://snyk.io/test/github/tj-django/django-clone/badge.svg?targetFile=requirements.txt)](https://snyk.io/test/github/tj-django/django-clone?targetFile=requirements.txt) | [![Codacy Badge](https://app.codacy.com/project/badge/Coverage/b33dd02dbb034d7fa9886a99f5383ea6)](https://www.codacy.com/gh/tj-django/django-clone?utm_source=github.com\&utm_medium=referral\&utm_content=tj-django/django-clone\&utm_campaign=Badge_Coverage) <br/> [![codecov](https://codecov.io/gh/tj-django/django-clone/branch/main/graph/badge.svg?token=2NE21Oe50Q)](https://codecov.io/gh/tj-django/django-clone)| [![Codacy Badge](https://app.codacy.com/project/badge/Grade/b33dd02dbb034d7fa9886a99f5383ea6)](https://www.codacy.com/gh/tj-django/django-clone?utm_source=github.com\&utm_medium=referral\&utm_content=tj-django/django-clone\&utm_campaign=Badge_Grade) | [![Updates](https://pyup.io/repos/github/tj-django/django-clone/shield.svg)](https://pyup.io/repos/github/tj-django/django-clone/) |  [![pre-commit.ci status](https://results.pre-commit.ci/badge/github/tj-django/django-clone/main.svg)](https://results.pre-commit.ci/latest/github/tj-django/django-clone/main) |

## django-clone

Create copies of a model instance with explicit control on how the instance should be duplicated (limiting fields or related objects copied) with unique field detection.

This solves the problem introduced by using `instance.pk = None` and `instance.save()` which results in copying more object state than required.

## Features

*   100% test coverage.
*   More control over how a model instance should be duplicated
*   Multi Database support i.e Create a duplicate on one or more databases.
*   Restrict fields used for creating a duplicate instance.
*   Detect unique fields and naively adds a suffix (`copy {count}`) to each new instance.

## Table of Contents

*   [Installation](#installation)
*   [Usage](#usage)
    *   [Subclassing the `CloneModel`](#subclassing-the-clonemodel)
    *   [Using the `CloneMixin`](#using-the-clonemixin)
    *   [Duplicating a model instance](#duplicating-a-model-instance)
        *   [Bulk cloning a model](#bulk-cloning-a-model)
        *   [Multi database support](#multi-database-support)
    *   [CloneMixin attributes](#clonemixin-attributes)
        *   [Explicit (include only these fields)](#explicit-include-only-these-fields)
        *   [Implicit (include all except these fields)](#implicit-include-all-except-these-fields)
    *   [Creating clones without subclassing `CloneMixin`.](#creating-clones-without-subclassing-clonemixin)
    *   [Django Admin](#django-admin)
        *   [Duplicating Models from the Django Admin view.](#duplicating-models-from-the-django-admin-view)
            *   [List View](#list-view)
            *   [Change View](#change-view)
        *   [CloneModelAdmin class attributes](#clonemodeladmin-class-attributes)
*   [Compatibility](#compatibility)
*   [Running locally](#running-locally)
*   [Found a Bug?](#found-a-bug)
*   [Contributors ✨](#contributors-)

## Installation

Run

```bash script
pip install django-clone
```

## Usage

### Subclassing the `CloneModel`

**CHANGE**

```python
from django.db import models

class MyModel(models.Model):
    title = models.CharField(max_length=200)
```

**TO**

```python
from django.db import models
from model_clone import CloneModel

class MyModel(CloneModel):
    title = models.CharField(max_length=200)
```

**Example**

```python
from django.db import models
from django.utils.translation import gettext_lazy as _
from model_clone import CloneModel

class TestModel(CloneModel):
    title = models.CharField(max_length=200)
    tags =  models.ManyToManyField('Tags')

    _clone_m2m_fields = ['tags']


class Tags(models.Model):  #  To enable cloning tags directly use `CloneModel` as shown above.
    name = models.CharField(max_length=255)

    def __str__(self):
        return _(self.name)
```

### Using the `CloneMixin`

```python
from django.db import models
from django.utils.translation import gettext_lazy as _
from model_clone import CloneMixin

class TestModel(CloneMixin, models.Model):
    title = models.CharField(max_length=200)
    tags =  models.ManyToManyField('Tags')

    _clone_m2m_fields = ['tags']


class Tags(models.Model):  #  To enable cloning tags directly use `CloneMixin` as shown above.
    name = models.CharField(max_length=255)

    def __str__(self):
        return _(self.name)
```

### Duplicating a model instance

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

In [6]: test_obj_clone = test_obj.make_clone()

In [7]: test_obj_clone.pk
Out[7]: 2

In [8]: test_obj_clone.title
Out[8]: 'New copy 1'

In [9]: test_obj_clone.tags.all()
Out[9]: <QuerySet [<Tag: men>, <Tag: women>]>

In [6]: test_obj_clone = test_obj.make_clone(attrs={'title': 'Updated title'})

In [7]: test_obj_clone.pk
Out[7]: 3

In [8]: test_obj_clone.title
Out[8]: 'Updated title'

In [9]: test_obj_clone.tags.all()
Out[9]: <QuerySet [<Tag: men>, <Tag: women>]>
```

#### Bulk cloning a model

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

In [6]: test_obj_clones = test_obj.bulk_clone(1000)

In [7]: len(test_obj_clones)
Out[7]: 1000

In [8]: test_obj_clone = test_obj_clones[0]

In [9]: test_obj_clone.pk
Out[9]: 2

In [10]: test_obj_clone.title
Out[10]: 'New copy 1'

In [11]: test_obj_clone.tags.all()
Out[11]: <QuerySet [<Tag: men>, <Tag: women>]>
```

#### Multi database support

```python

In [6]: test_obj_clone = test_obj.make_clone(using='replica')  # Replicate test object to a different database.

In [7]: test_obj_clone.pk
Out[7]: 1

In [8]: test_obj_clone.title
Out[8]: 'New'

In [9]: test_obj_clone.tags.all()
Out[9]: <QuerySet [<Tag: men>, <Tag: women>]>

In [10]: test_obj_clone._state.db
Out[10]: 'replica'
```

### CloneMixin attributes

|    Attribute        |  Description |
|:------------------------------:|:------------:|
| `DUPLICATE_SUFFIX` | Suffix to append to duplicates <br> (NOTE: This requires `USE_DUPLICATE_SUFFIX_FOR_NON_UNIQUE_FIELDS` <br> to be enabled and supports string fields). |
`USE_DUPLICATE_SUFFIX_FOR_NON_UNIQUE_FIELDS` | Enable appending the `DUPLICATE_SUFFIX` to new cloned instances. |
`UNIQUE_DUPLICATE_SUFFIX` | Suffix to append to unique fields |
`USE_UNIQUE_DUPLICATE_SUFFIX` | Enable appending the `UNIQUE_DUPLICATE_SUFFIX` to new cloned instances. |
`MAX_UNIQUE_DUPLICATE_QUERY_ATTEMPTS` | The max query attempt while generating unique values for a case of unique conflicts. |

#### Explicit (include only these fields)

|    Attribute        |  Description |
|:------------------------------:|:------------:|
| `_clone_fields` | Restrict the list of fields to copy from the instance (By default: Copies all fields excluding auto-created/non editable model fields) |
`_clone_m2m_fields` | Restricted Many to many fields (i.e Test.tags) |
`_clone_m2o_or_o2m_fields` | Restricted Many to One/One to Many fields |
`_clone_o2o_fields` | Restricted One to One fields |

#### Implicit (include all except these fields)

|  Attribute  | Description |
|:--------------------:|:-----------:|
| `_clone_excluded_fields` | Excluded model fields. |
`_clone_excluded_m2m_fields` | Excluded many to many fields. |
`_clone_excluded_m2o_or_o2m_fields` |  Excluded Many to One/One to Many fields. |
`_clone_excluded_o2o_fields` | Excluded one to one fields. |

> **NOTE:** :warning:
>
> *   Ensure to either set `_clone_excluded_*` or `_clone_*`. Using both would raise errors.

### Creating clones without subclassing `CloneMixin`.

```python

In [1]: from model_clone.utils import create_copy_of_instance

In [2]: test_obj = TestModel.objects.create(title='New')

In [3]: test_obj.pk
Out[3]: 1

In [4]: test_obj.title
Out[4]: 'New'

In [5]: test_obj.tags.create(name='men')

In [6]: test_obj.tags.create(name='women')

In [7]: test_obj.tags.all()
Out[7]: <QuerySet [<Tag: men>, <Tag: women>]>

In [8]: test_obj_clone = create_copy_of_instance(test_obj, attrs={'title': 'Updated title'})

In [9]: test_obj_clone.pk
Out[9]: 2

In [10]: test_obj_clone.title
Out[10]: 'Updated title'

In [11]: test_obj_clone.tags.all()
Out[11]: <QuerySet []>
```

> **NOTE:** :warning:
>
> *   This method won't copy over related objects like Many to Many/One to Many relationships.
> *   Ensure that required fields skipped from being cloned are passed in using the `attrs` kwargs.

### Django Admin

#### Duplicating Models from the Django Admin view.

**Change**

```python
from django.contrib import admin
from django.contrib.admin import ModelAdmin

@admin.register(TestModel)
class TestModelAdmin(ModelAdmin):
    pass
```

**to**

```python
from model_clone import CloneModelAdmin

@admin.register(TestModel)
class TestModelAdmin(CloneModelAdmin):
    pass
```

##### List View

![Screenshot](Duplicate-action.png)

##### Change View

![Screenshot](Duplicate-button.png)

#### CloneModelAdmin class attributes

```python

from model_clone import CloneModelAdmin

@admin.register(TestModel)
class TestModelAdmin(CloneModelAdmin):
    # Enables/Disables the Duplicate action in the List view (Defaults to True)
    include_duplicate_action = True
    # Enables/Disables the Duplicate action in the Change view (Defaults to True)
    include_duplicate_object_link = True
```

> **NOTE:** :warning:
>
> *   Ensure that `model_clone` is placed before `django.contrib.admin`

```python
INSTALLED_APPS = [
    'model_clone',
    'django.contrib.admin',
    '...',
]
```

## Compatibility

|  Python      |  Supported version |
|--------------|--------------------|
|  Python2.x  |    `<=2.5.3`       |
|  Python3.5  |    `<=2.9.6`       |
|  Python3.6+  |    All versions    |

|  Django      |   Supported version |
|--------------|---------------------|
|  1.11        |    `<=2.7.2`        |
|  2.x         |    All versions     |
|  3.x         |    All versions     |

## Running locally

```shell
$ git clone git@github.com:tj-django/django-clone.git
$ make default-user
$ make run
```

Spins up a django server running the demo app.

Visit http://127.0.0.1:8000

## Found a Bug?

To file a bug or submit a patch, please head over to [django-clone on github](https://github.com/tj-django/django-clone/issues).

If you feel generous and want to show some extra appreciation:

Support me with a :star:

[![Buy me a coffee][buymeacoffee-shield]][buymeacoffee]

[buymeacoffee]: https://www.buymeacoffee.com/jackton1

[buymeacoffee-shield]: https://www.buymeacoffee.com/assets/img/custom_images/orange_img.png

## Contributors ✨

Thanks goes to these wonderful people:

<!-- ALL-CONTRIBUTORS-LIST:START - Do not remove or modify this section -->

<!-- prettier-ignore-start -->

<!-- markdownlint-disable -->

<table>
  <tr>
    <td align="center"><a href="http://gerritneven.nl"><img src="https://avatars1.githubusercontent.com/u/2500973?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Gerben Neven</b></sub></a><br /><a href="https://github.com/tj-django/django-clone/issues?q=author%3Agerbyzation" title="Bug reports">🐛</a> <a href="https://github.com/tj-django/django-clone/commits?author=gerbyzation" title="Tests">⚠️</a> <a href="https://github.com/tj-django/django-clone/commits?author=gerbyzation" title="Code">💻</a></td>
    <td align="center"><a href="http://sebastian-kindt.com"><img src="https://avatars1.githubusercontent.com/u/2536081?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Sebastian Kapunkt</b></sub></a><br /><a href="https://github.com/tj-django/django-clone/commits?author=SebastianKapunkt" title="Code">💻</a> <a href="https://github.com/tj-django/django-clone/issues?q=author%3ASebastianKapunkt" title="Bug reports">🐛</a> <a href="https://github.com/tj-django/django-clone/commits?author=SebastianKapunkt" title="Tests">⚠️</a></td>
    <td align="center"><a href="https://github.com/andresp99999"><img src="https://avatars0.githubusercontent.com/u/1036725?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Andrés Portillo</b></sub></a><br /><a href="https://github.com/tj-django/django-clone/issues?q=author%3Aandresp99999" title="Bug reports">🐛</a></td>
    <td align="center"><a href="https://renovate.whitesourcesoftware.com"><img src="https://avatars0.githubusercontent.com/u/25180681?v=4?s=100" width="100px;" alt=""/><br /><sub><b>WhiteSource Renovate</b></sub></a><br /><a href="#maintenance-renovate-bot" title="Maintenance">🚧</a></td>
    <td align="center"><a href="https://github.com/yuekui"><img src="https://avatars2.githubusercontent.com/u/2561450?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Yuekui</b></sub></a><br /><a href="https://github.com/tj-django/django-clone/commits?author=yuekui" title="Code">💻</a> <a href="https://github.com/tj-django/django-clone/issues?q=author%3Ayuekui" title="Bug reports">🐛</a> <a href="https://github.com/tj-django/django-clone/commits?author=yuekui" title="Tests">⚠️</a></td>
    <td align="center"><a href="https://github.com/diesieben07"><img src="https://avatars.githubusercontent.com/u/1915984?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Take Weiland</b></sub></a><br /><a href="https://github.com/tj-django/django-clone/commits?author=diesieben07" title="Tests">⚠️</a> <a href="https://github.com/tj-django/django-clone/issues?q=author%3Adiesieben07" title="Bug reports">🐛</a> <a href="https://github.com/tj-django/django-clone/commits?author=diesieben07" title="Code">💻</a></td>
    <td align="center"><a href="https://github.com/ptrck"><img src="https://avatars.githubusercontent.com/u/1259703?v=4?s=100" width="100px;" alt=""/><br /><sub><b>Patrick</b></sub></a><br /><a href="https://github.com/tj-django/django-clone/issues?q=author%3Aptrck" title="Bug reports">🐛</a> <a href="https://github.com/tj-django/django-clone/commits?author=ptrck" title="Code">💻</a></td>
  </tr>
</table>

<!-- markdownlint-restore -->

<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->

This project follows the [all-contributors](https://github.com/all-contributors/all-contributors) specification. Contributions of any kind welcome!
