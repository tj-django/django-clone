<p align="center"> 
    <img width="466" alt="4FC889E9-FF59-4E44-9EB6-2AF7DC034C74" src="https://user-images.githubusercontent.com/17484350/215616634-17439a58-7bd8-4e9c-989f-e6bef7c73e48.png">
</p>

|  Python   | Django  |  Downloads  |   Code Style   |
|:---------:|:-------:|:-----------:|:--------------:|
| [![PyPI - Python Version](https://img.shields.io/pypi/pyversions/django_clone.svg)](https://pypi.org/project/django-clone) | [![PyPI - Django Version](https://img.shields.io/pypi/djversions/django_clone.svg)](https://docs.djangoproject.com/en/3.2/releases/) | [![Downloads](https://pepy.tech/badge/django-clone)](https://pepy.tech/project/django-clone) | [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black) |

|    PyPI         | Test | Vulnerabilities | Coverage | Code Quality  |  Pre-Commit   |
|:---------------:|:----:|:---------------:|:--------:|:-------------:|:-------------:|
| [![PyPI version](https://badge.fury.io/py/django-clone.svg)](https://badge.fury.io/py/django-clone) | [![Test](https://github.com/tj-django/django-clone/workflows/Test/badge.svg)](https://github.com/tj-django/django-clone/actions?query=workflow%3ATest) | [![Known Vulnerabilities](https://snyk.io/test/github/tj-django/django-clone/badge.svg?targetFile=requirements.txt)](https://snyk.io/test/github/tj-django/django-clone?targetFile=requirements.txt) | [![Codacy Badge](https://app.codacy.com/project/badge/Coverage/b33dd02dbb034d7fa9886a99f5383ea6)](https://www.codacy.com/gh/tj-django/django-clone?utm_source=github.com\&utm_medium=referral\&utm_content=tj-django/django-clone\&utm_campaign=Badge_Coverage) <br/> [![codecov](https://codecov.io/gh/tj-django/django-clone/branch/main/graph/badge.svg?token=2NE21Oe50Q)](https://codecov.io/gh/tj-django/django-clone)| [![Codacy Badge](https://app.codacy.com/project/badge/Grade/b33dd02dbb034d7fa9886a99f5383ea6)](https://www.codacy.com/gh/tj-django/django-clone?utm_source=github.com\&utm_medium=referral\&utm_content=tj-django/django-clone\&utm_campaign=Badge_Grade) |  [![pre-commit.ci status](https://results.pre-commit.ci/badge/github/tj-django/django-clone/main.svg)](https://results.pre-commit.ci/latest/github/tj-django/django-clone/main) |

## django-clone

Create copies of a model instance with explicit control on how the instance should be duplicated (limiting fields or related objects copied) with unique field detection.

This solves the problem introduced by using `instance.pk = None` and `instance.save()` which results in copying more object state than required.

## Features

*   100% test coverage.
*   More control over how a model instance should be duplicated
*   Multi Database support i.e Create duplicates on one or more databases.
*   Restrict fields used for creating a duplicate instance.
*   Detects unique fields and naively adds a suffix `copy {count}` to each duplicate instance (for supported fields only).
*   Optionally differentiate between a duplicate instance and the original by appending a **copy** suffix to non unique fields (for supported fields only).

## Table of Contents

*   [Installation](#installation)
*   [Usage](#usage)
    *   [Subclassing the `CloneModel`](#subclassing-the-clonemodel)
    *   [Using the `CloneMixin`](#using-the-clonemixin)
    *   [Duplicating a model instance](#duplicating-a-model-instance)
    *   [Bulk cloning a model](#bulk-cloning-a-model)
    *   [Creating clones without subclassing `CloneMixin`.](#creating-clones-without-subclassing-clonemixin)
    *   [CloneMixin attributes](#clonemixin-attributes)
        *   [Explicit (include only these fields)](#explicit-include-only-these-fields)
        *   [Implicit (include all except these fields)](#implicit-include-all-except-these-fields)
    *   [Django Admin](#django-admin)
        *   [Duplicating Models from the Django Admin view.](#duplicating-models-from-the-django-admin-view)
            *   [List View](#list-view)
            *   [Change View](#change-view)
        *   [CloneModelAdmin class attributes](#clonemodeladmin-class-attributes)
*   [Advanced Usage](#advanced-usage)
    *   [Signals](#signals)
        *   [pre\_clone\_save, post\_clone\_save](#pre_clone_save-post_clone_save)
    *   [Clone Many to Many fields](#clone-many-to-many-fields)
        *   [Using the `CloneModel`](#using-the-clonemodel)
        *   [Using the `CloneMixin`](#using-the-clonemixin-1)
    *   [Multi database support](#multi-database-support)
*   [Compatibility](#compatibility)
*   [Running locally](#running-locally)
*   [Found a Bug?](#found-a-bug)
*   [Contributors ✨](#contributors-)

## Installation

![](https://user-images.githubusercontent.com/17484350/221386740-aa66df70-eed0-40ed-9c5f-1d3b6c9045c2.png)

## Usage

### Subclassing the `CloneModel`

![](https://user-images.githubusercontent.com/17484350/221387430-efd5508a-2597-4320-9750-5a4c56833edb.png)

### Using the `CloneMixin`

![](https://user-images.githubusercontent.com/17484350/221387397-6ad5475b-6887-4a5f-b6d3-42784f9dfa7c.png)

### Duplicating a model instance

![](https://user-images.githubusercontent.com/17484350/221386600-731a6f45-1704-4834-bcbe-0f57d912faf7.png)

### Bulk cloning a model

![](https://user-images.githubusercontent.com/17484350/221386555-13978280-35a1-4941-8186-a1c6723a0346.png)

### Creating clones without subclassing `CloneMixin`.

> **NOTE:** :warning:
>
> *   This method won't copy over related objects like Many to Many/One to Many relationships.
> *   Ensure that required fields skipped from being cloned are passed in using the `attrs` kwargs.

![](https://user-images.githubusercontent.com/17484350/221385171-add1a0c3-21fc-4c48-bfe9-4f2014ffe035.png)

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
| `_clone_m2m_fields` | Restricted Many to many fields (i.e Test.tags) |
| `_clone_m2o_or_o2m_fields` | Restricted Many to One/One to Many fields |
| `_clone_o2o_fields` | Restricted One to One fields |
| `_clone_linked_m2m_fields` | Restricted Many to Many fields that should be linked to the new instance |

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

### Django Admin

#### Duplicating Models from the Django Admin view.

![](https://user-images.githubusercontent.com/17484350/221386874-047989a4-ae4d-4d82-9ef6-2b303001a4c2.png)

##### List View

![Screenshot](Duplicate-action.png)

##### Change View

![Screenshot](Duplicate-button.png)

#### CloneModelAdmin class attributes

![](https://user-images.githubusercontent.com/17484350/221387085-e0ca31ee-8c4c-40d9-9ce6-44ff5e6814ff.png)

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

## Advanced Usage

### Signals

#### pre\_clone\_save, post\_clone\_save

![](https://user-images.githubusercontent.com/17484350/221387120-b5219cdb-9f74-4751-b593-2c68db9fd0e0.png)

### Clone Many to Many fields

#### Using the `CloneModel`

![](https://user-images.githubusercontent.com/17484350/221387226-572cedbe-e30e-456d-af75-bcd25edec754.png)

#### Using the `CloneMixin`

![carbon (37)](https://user-images.githubusercontent.com/17484350/221387393-196bcb4b-e136-4d5b-89cd-0fb28d8e6e6e.png)

![](https://user-images.githubusercontent.com/17484350/221387265-ccf05239-ec0c-47ec-b0ed-6c2e01428aee.png)

### Multi database support

![](https://user-images.githubusercontent.com/17484350/221385217-3a123080-b247-4ef0-b876-e75db1518c92.png)

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
  <tbody>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="http://gerritneven.nl"><img src="https://avatars1.githubusercontent.com/u/2500973?v=4?s=100" width="100px;" alt="Gerben Neven"/><br /><sub><b>Gerben Neven</b></sub></a><br /><a href="https://github.com/tj-django/django-clone/issues?q=author%3Agerbyzation" title="Bug reports">🐛</a> <a href="https://github.com/tj-django/django-clone/commits?author=gerbyzation" title="Tests">⚠️</a> <a href="https://github.com/tj-django/django-clone/commits?author=gerbyzation" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="http://sebastian-kindt.com"><img src="https://avatars1.githubusercontent.com/u/2536081?v=4?s=100" width="100px;" alt="Sebastian Kapunkt"/><br /><sub><b>Sebastian Kapunkt</b></sub></a><br /><a href="https://github.com/tj-django/django-clone/commits?author=SebastianKapunkt" title="Code">💻</a> <a href="https://github.com/tj-django/django-clone/issues?q=author%3ASebastianKapunkt" title="Bug reports">🐛</a> <a href="https://github.com/tj-django/django-clone/commits?author=SebastianKapunkt" title="Tests">⚠️</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/andresp99999"><img src="https://avatars0.githubusercontent.com/u/1036725?v=4?s=100" width="100px;" alt="Andrés Portillo"/><br /><sub><b>Andrés Portillo</b></sub></a><br /><a href="https://github.com/tj-django/django-clone/issues?q=author%3Aandresp99999" title="Bug reports">🐛</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://renovate.whitesourcesoftware.com"><img src="https://avatars0.githubusercontent.com/u/25180681?v=4?s=100" width="100px;" alt="WhiteSource Renovate"/><br /><sub><b>WhiteSource Renovate</b></sub></a><br /><a href="#maintenance-renovate-bot" title="Maintenance">🚧</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/yuekui"><img src="https://avatars2.githubusercontent.com/u/2561450?v=4?s=100" width="100px;" alt="Yuekui"/><br /><sub><b>Yuekui</b></sub></a><br /><a href="https://github.com/tj-django/django-clone/commits?author=yuekui" title="Code">💻</a> <a href="https://github.com/tj-django/django-clone/issues?q=author%3Ayuekui" title="Bug reports">🐛</a> <a href="https://github.com/tj-django/django-clone/commits?author=yuekui" title="Tests">⚠️</a> <a href="https://github.com/tj-django/django-clone/commits?author=yuekui" title="Documentation">📖</a> <a href="#maintenance-yuekui" title="Maintenance">🚧</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/diesieben07"><img src="https://avatars.githubusercontent.com/u/1915984?v=4?s=100" width="100px;" alt="Take Weiland"/><br /><sub><b>Take Weiland</b></sub></a><br /><a href="https://github.com/tj-django/django-clone/commits?author=diesieben07" title="Tests">⚠️</a> <a href="https://github.com/tj-django/django-clone/issues?q=author%3Adiesieben07" title="Bug reports">🐛</a> <a href="https://github.com/tj-django/django-clone/commits?author=diesieben07" title="Code">💻</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/ptrck"><img src="https://avatars.githubusercontent.com/u/1259703?v=4?s=100" width="100px;" alt="Patrick"/><br /><sub><b>Patrick</b></sub></a><br /><a href="https://github.com/tj-django/django-clone/issues?q=author%3Aptrck" title="Bug reports">🐛</a> <a href="https://github.com/tj-django/django-clone/commits?author=ptrck" title="Code">💻</a></td>
    </tr>
    <tr>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/Akollek"><img src="https://avatars.githubusercontent.com/u/5873158?v=4?s=100" width="100px;" alt="Amiel Kollek"/><br /><sub><b>Amiel Kollek</b></sub></a><br /><a href="https://github.com/tj-django/django-clone/commits?author=Akollek" title="Code">💻</a> <a href="https://github.com/tj-django/django-clone/issues?q=author%3AAkollek" title="Bug reports">🐛</a> <a href="https://github.com/tj-django/django-clone/commits?author=Akollek" title="Tests">⚠️</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://erictheise.com/"><img src="https://avatars.githubusercontent.com/u/317680?v=4?s=100" width="100px;" alt="Eric Theise"/><br /><sub><b>Eric Theise</b></sub></a><br /><a href="https://github.com/tj-django/django-clone/commits?author=erictheise" title="Documentation">📖</a></td>
      <td align="center" valign="top" width="14.28%"><a href="https://github.com/DanielSchaffer"><img src="https://avatars.githubusercontent.com/u/334487?v=4?s=100" width="100px;" alt="Daniel Schaffer"/><br /><sub><b>Daniel Schaffer</b></sub></a><br /><a href="https://github.com/tj-django/django-clone/commits?author=DanielSchaffer" title="Code">💻</a> <a href="https://github.com/tj-django/django-clone/commits?author=DanielSchaffer" title="Tests">⚠️</a></td>
    </tr>
  </tbody>
</table>

<!-- markdownlint-restore -->

<!-- prettier-ignore-end -->

<!-- ALL-CONTRIBUTORS-LIST:END -->

This project follows the [all-contributors](https://github.com/all-contributors/all-contributors) specification. Contributions of any kind welcome!
