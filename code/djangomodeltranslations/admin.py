from typing import Any
from copy import copy

from django.contrib import admin
from django import forms

from django.db.models.query import QuerySet
from django.http import HttpRequest
from django.contrib.admin.utils import flatten_fieldsets
from django.shortcuts import redirect
from functools import partial

from django.forms.models import (
    BaseInlineFormSet,
    inlineformset_factory,
    modelform_defines_fields,
    modelform_factory,
    modelformset_factory,
)
from django.core.exceptions import FieldError


from language_details import SITE_LANGUAGE_CODES, SITE_LANGUAGE_DEFAULT_CODE

# Register your models here.
ADMIN_LINK = "/admin-solar/"

class LangModelAdmin(admin.ModelAdmin):
    """
    A specialized ModelAdmin that enhances the Django admin interface to support
    translatable fields for models inheriting from `TranslationModel`.

    Key Features:

    *   Filtering: Filters the queryset to display only objects in the default language.

    *   Field Exclusion: Excludes the `lang` and `original` fields from the admin form.

    *   Add View: Handles the creation of new objects and their translations.

    *   Change View: Manages the editing of existing objects and their translations.

    *   Form Customization: Dynamically adds translation fields to the admin form,
        providing separate input fields for each language and pre-populating
        them with existing translation data.

    *   Media: Includes custom JavaScript and CSS for the enhanced admin interface.
    """

    list_filter = ("lang",)

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        """
        Filters the queryset to display only objects in the default language.

        Args:
            request: The current HTTP request.

        Returns:
            A QuerySet containing objects in the default language.
        """
        qs = super().get_queryset(request)
        return qs.filter(lang=SITE_LANGUAGE_DEFAULT_CODE)

    def get_exclude(self, request, obj=None):
        """
        Excludes the `lang` and `original` fields from the admin form.

        Args:
            request: The current HTTP request.
            obj: The model instance being edited (optional).

        Returns:
            A list of fields to exclude from the admin form.
        """
        exclude_fields = super().get_exclude(request, obj)
        if exclude_fields is None:
            exclude_fields = []
        exclude_fields.extend(["lang", "original"])
        return exclude_fields

    def add_view(self, request, form_url="", extra_context=None):
        """
        Handles the creation of a new object and its translations.

        Args:
            request: The current HTTP request.
            form_url: The URL for the admin form (optional).
            extra_context: Additional context data for the template (optional).
        """
        if request.method != "POST":
            return super().add_view(request, form_url, extra_context)

        obj = None
        fieldsets = self.get_fieldsets(request, obj)
        ModelForm = self.get_form(
            request,
            None,
            change=False,
            fields=flatten_fieldsets(fieldsets)
        )
        form = ModelForm(request.POST, request.FILES, instance=obj)

        if not form.is_valid():
            return super().add_view(request, form_url, extra_context)

        obj = form.save(commit=False)

        obj.lang = SITE_LANGUAGE_DEFAULT_CODE
        obj.save()
        original_id = obj.id

        # Optimization: Fetch all existing translations once to avoid repeated queries
        existing_translations = {trans.lang: trans for trans in obj.translations.all()}

        for lang, _ in SITE_LANGUAGE_CODES:
            if lang == SITE_LANGUAGE_DEFAULT_CODE:
                continue

            # Optimization: Reuse existing translation object if available
            translation = existing_translations.get(lang)
            if translation:
                obj = translation 
            else:
                obj.id = None 

            obj.original_id = original_id
            obj.lang = lang

            for fieldname in self.model.translate_fields:
                setattr(obj, fieldname, form.cleaned_data[f"{fieldname}_{lang}"])

            obj.save()

        return redirect(ADMIN_LINK)

    def change_view(
            self,
            request,
            object_id,
            form_url="",
            extra_context=None
        ):
        """
        Handles the editing of an existing object and its translations.

        Args:
            request: The current HTTP request.
            object_id: The ID of the object being edited.
            form_url: The URL for the admin form (optional).
            extra_context: Additional context data for the template (optional).
        """
        obj = self.get_object(request, object_id)

        # Optimization: Fetch all existing translations once to avoid repeated queries
        existing_translations = {trans.lang: trans for trans in obj.translations.all()}

        if request.method != "POST":
            return super().change_view(request, object_id, form_url, extra_context)

        ModelForm = self.get_form(request, obj)
        form = ModelForm(request.POST, request.FILES, instance=obj)

        if not form.is_valid():
            return super().change_view(request, object_id, form_url, extra_context)

        obj = form.save(commit=False)
        obj.save()

        original_id = obj.id

        for lang, _ in SITE_LANGUAGE_CODES:
            if lang == SITE_LANGUAGE_DEFAULT_CODE:
                continue

            # Optimization: Reuse existing translation object if available
            translation = existing_translations.get(lang)
            if translation:
                obj = translation
            else:
                obj.id = None 

            obj.original_id = original_id
            obj.lang = lang

            for fieldname in self.model.translate_fields:
                setattr(obj, fieldname, form.cleaned_data[f"{fieldname}_{lang}"])

            obj.save()

        return redirect(ADMIN_LINK)

    def get_form(self, request, obj=None, change=False, **kwargs):
        """
        Returns a Form class for use in the admin add/change views.

        This method dynamically adds translation fields to the form based on
        the model's `translate_fields` attribute and pre-populates them with
        existing translation data (if available).

        Args:
            request: The current HTTP request.
            obj: The model instance being edited (optional).
            change: Indicates whether this is a change form (True) or an add form (False).
            **kwargs: Additional keyword arguments.

        Returns:
            A dynamically generated Form class with translation fields.
        """
        if "fields" in kwargs:
            fields = kwargs.pop("fields")
        else:
            fields = flatten_fieldsets(self.get_fieldsets(request, obj))
        excluded = self.get_exclude(request, obj)
        exclude = [] if excluded is None else list(excluded)
        readonly_fields = self.get_readonly_fields(request, obj)
        exclude.extend(readonly_fields)
        # Exclude all fields if it's a change form and the user doesn't have
        # the change permission.
        if (
            change
            and hasattr(request, "user")
            and not self.has_change_permission(request, obj)
        ):
            exclude.extend(fields)
        if excluded is None and hasattr(self.form, "_meta") and self.form._meta.exclude:
            # Take the custom ModelForm's Meta.exclude into account only if the
            # ModelAdmin doesn't define its own.
            exclude.extend(self.form._meta.exclude)
        # if exclude is an empty list we pass None to be consistent with the
        # default on modelform_factory
        exclude = exclude or None

        # Remove declared form fields which are in readonly_fields.
        new_attrs = dict.fromkeys(
            f for f in readonly_fields if f in self.form.declared_fields
        )

        for lang, _ in SITE_LANGUAGE_CODES:
            if lang == SITE_LANGUAGE_DEFAULT_CODE:
                continue

            for field in self.model.translate_fields:
                lang_field = copy.copy(self.form.base_fields[f"{field}"])
                lang_field.label = lang_field.label + f" ({lang})"


                new_attrs[f"{field}_{lang}"] = lang_field
        form = type(self.form.__name__, (self.form,), new_attrs)

        defaults = {
            "form": form,
            "fields": fields,
            "exclude": exclude,
            "formfield_callback": partial(self.formfield_for_dbfield, request=request),
            **kwargs,
        }

        if defaults["fields"] is None and not modelform_defines_fields(
            defaults["form"]
        ):
            defaults["fields"] = forms.ALL_FIELDS

        try:
            return modelform_factory(self.model, **defaults)
        except FieldError as e:
            raise FieldError(
                "%s. Check fields/fieldsets/exclude attributes of class %s."
                % (e, self.__class__.__name__)
            )
    
    class Media:
        js = ("/static/admin-lang/main.js",)
        css = {"all": ["/static/admin-lang/main.css"]}
