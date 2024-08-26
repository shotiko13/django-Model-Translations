import json

from django import forms
from language_details import SITE_LANGUAGE_CODES, SITE_LANGUAGE_DEFAULT_CODE


class LangModelForm(forms.ModelForm):
    """
    A specialized ModelForm that facilitates the handling of translatable fields.

    This form automatically incorporates additional fields for each translatable field
    specified in the model's `translate_fields` attribute. It ensures proper initialization
    and pre-population of these fields based on existing translations, streamlining the
    process of managing multilingual content.

    Key Features:

    *   `translate_fields`: A hidden `CharField` that stores a JSON-serialized list
        of the model's translatable fields.

    *   Dynamic Field Generation:  Upon initialization, the form dynamically creates
        additional fields for each translatable field and language combination, enabling
        separate input for each translation.

    *   Translation Pre-population:  When editing an existing object, the form retrieves
        existing translations and pre-populates the corresponding translation fields,
        providing a convenient editing experience.

    Example Usage:

    ```python
    from django import forms
    from .models import MyTranslatableModel  # Import your translatable model

    class MyTranslatableModelForm(LangModelForm):
        class Meta:
            model = MyTranslatableModel
            fields = '__all__'  # Or specify the fields you want in the form
    ```

    **Important Considerations:**

    *   The model associated with this form must have a `translate_fields` attribute
        defining the list of translatable fields.

    *   Ensure that your `SITE_LANGUAGE_CODES` and `SITE_LANGUAGE_DEFAULT_CODE`
        are correctly defined in your `language_details` module.
    """

    translate_fields = forms.CharField(
        label="translate fields", widget=forms.HiddenInput()
    )

    def __init__(self, *args, **kwargs) -> None:
        """
        Initializes the form, dynamically adding translation fields and pre-populating
        them with existing translation data (if available).

        Args:
            *args: Positional arguments passed to the parent `ModelForm.__init__` method.
            **kwargs: Keyword arguments passed to the parent `ModelForm.__init__` method.
        """
        super().__init__(*args, **kwargs)

        if self.initial is None:
            self.initial = {}

        self.initial["translate_fields"] = json.dumps(
            self._meta.model.translate_fields
        )

        if self.instance is not None and self.instance.pk is not None:
            translated_objs = {o.lang: o for o in self.instance.translations
            .filter(original_id=self.instance.id)}

            for lang, _ in SITE_LANGUAGE_CODES:
                if lang == SITE_LANGUAGE_DEFAULT_CODE:
                    continue
                translation = translated_objs.get(lang)

                for field in self._meta.model.translate_fields:
                    changing_field = f"{field}_{lang}"
                    if hasattr(translation, field):
                        self.initial[changing_field] = getattr(translation, field)