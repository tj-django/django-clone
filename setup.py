import io
import os

from setuptools import find_namespace_packages, setup

install_requires = [
    "django",
    "future>=0.17.1",
    "conditional>=1.3",
    "six",
]

test_requires = [
    "tox",
    "tox-gh-actions",
    "pluggy>=0.7",
    "mock",
    "unittest-xml-reporting",
    "codacy-coverage",
    "django-migration-fixer",
]

deploy_requires = [
    "bump2version",
    "readme_renderer[md]",
    "git-changelog",
]


local_dev_requires = [
    "pip-tools",
    "check-manifest",
]

extras_require = {
    "development": [
        local_dev_requires,
        install_requires,
        test_requires,
        deploy_requires,
    ],
    "test": test_requires,
    "deploy": deploy_requires,
}

BASE_DIR = os.path.dirname(__file__)
README_PATH = os.path.join(BASE_DIR, "README.md")
LONG_DESCRIPTION_TYPE = "text/markdown"

if os.path.isfile(README_PATH):
    with io.open(README_PATH, encoding="utf-8") as f:
        LONG_DESCRIPTION = f.read()
else:
    LONG_DESCRIPTION = ""

setup(
    name="django-clone",
    version="5.0.0",
    description="Create a clone of a django model instance.",
    python_requires=">=3.6",
    long_description=LONG_DESCRIPTION,
    long_description_content_type=LONG_DESCRIPTION_TYPE,
    author="Tonye Jack",
    author_email="jtonye@ymail.com",
    maintainer="Tonye Jack",
    maintainer_email="jtonye@ymail.com",
    url="https://github.com/tj-django/django-clone.git",
    license="MIT/Apache-2.0",
    zip_safe=False,
    include_package_data=True,
    keywords=[
        "django",
        "django-clone",
        "django clone",
        "django object clone",
        "clone-django",
        "model cloning",
        "django instance duplication",
        "django duplication",
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        "Topic :: Internet :: WWW/HTTP",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Framework :: Django :: 2.0",
        "Framework :: Django :: 2.1",
        "Framework :: Django :: 2.2",
        "Framework :: Django :: 3.0",
        "Framework :: Django :: 3.1",
        "Framework :: Django :: 3.2",
        "Framework :: Django :: 4.0",
        "Framework :: Django :: 4.1",
    ],
    install_requires=install_requires,
    tests_require=["coverage"],
    extras_require=extras_require,
    packages=find_namespace_packages(
        include=[
            "model_clone.templates.admin",
            "model_clone",
            "model_clone.templates.clone",
        ],
    ),
)
