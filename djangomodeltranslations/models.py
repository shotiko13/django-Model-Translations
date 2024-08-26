from django.db import models
from django.utils.translation import gettext_lazy as _
from language_details import SITE_LANGUAGE_DEFAULT_CODE

# Create your models here.

class TranslationModel(models.Model):
    """
    An abstract base class for models that require translation support.

    This class provides two fields: `lang` and `original`.

    *  **`lang`**: A `CharField` representing the language code of the translation.
        Defaults to the `SITE_LANGUAGE_DEFAULT_CODE`.

    *  **`original`**: A self-referential `ForeignKey` to the original (untranslated) instance
    of the model. This field allows you to link translations to their corresponding original.

    Subclasses of `TranslationModel` must be abstract, as they provide the foundation for
    translation functionality but do not represent concrete data models themselves.

    **Important:**

    *   The `Meta` class defines this model as `abstract`, meaning it cannot be instantiated
        directly. Instead, it serves as a base class for other models that require
        translation support.

    *   The `indexes` attribute creates a database index on the `original` and `lang` fields,
        optimizing queries that filter by these fields.
    """

    lang = models.CharField(
        "Language", max_length=3,
        default=SITE_LANGUAGE_DEFAULT_CODE,
        blank=False,
        null=False,
    )

    original = models.ForeignKey(
        "self",
        verbose_name=_("Original"),
        null=True,
        blank=True,
        related_name="translations",
        on_delete=models.CASCADE,
    )

    class Meta:
        abstract = True
        indexes = [models.Index(fields=["original", "lang"])]