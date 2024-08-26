
## Installation

```bash
pip install django-modeltranslation-admin


# Django model translation

This package provides some custom translation functionality.
## Installation

To install the package by `pip` run following command

```sh
# From Github (latest updates)
$ pip install git+https://github.com/shotiko13/django-Model-Translations
# Or
$ pip install django-modeltranslations
```

## Usage

To start using the package in your project, you need to open `settings.py` file and add following lines

```python
# settings.py
from pathlib import Path

# Application definition

INSTALLED_APPS = [
    ...
    'django-modeltranslations',
    ...
]

SITE_LANGUAGE_DEFAULT_CODE = "ka" # your choice of language
SITE_LANGUAGE_CODES = [("ka", "ქართული"), ("en", "ინგლისური")] # add as many as u wish


MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "static"

```

### translations admin

To use translations in admin we need to extend our admin class with TranslationAdmin


```python
@admin.register(Project)
class ProjectAdmin(LangModelAdmin):
    #write anything else you wish
```

### Translation Models

```python
# models.py
class ContentBaseModel(MetaInfo, BaseModel, TranslationModel):

    translate_fields = ["title", "description"]

    title = models.CharField("სათაური", max_length=400, null=True)   

    image = models.JSONField("სურათი", null=True)

    description = models.TextField("აღწერა", default="")


# forms.py
from django import forms
from django-modeltranslations import LangModelForm
from .models import JSONModel

class ProductForm(LangModelForm):
    class Meta:
        model = Product
        fields = "__all__"

        widgets = {
            "image": ImageWidget(),
            "description": TinymceWidget(),
            "video_up": VideoWidget(),
            "video_down": VideoWidget(),
        }



```