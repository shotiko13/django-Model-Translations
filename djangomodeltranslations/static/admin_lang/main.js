function addLangTabs(form, site_language_default_code, site_language_codes) {
    let fieldset = form.querySelector("fieldset");

    const tabsElement = document.createElement("div");

    tabsElement.classList.add("form-row");
    tabsElement.classList.add("form-lang-row");

    let rows = Array.from(form.querySelectorAll(".form-row"));

    tabsElement.innerHTML = site_language_codes
        .map(([lang, langname]) => {
            if (lang == site_language_default_code) {
                return `<button class="lang-tab-btn selected" data-lang="${lang}" type="button">${langname}</button>`;
            }

            return `<button class="lang-tab-btn" data-lang="${lang}" type="button">${langname}</button>`;
        })
        .join("");

    fieldset.insertBefore(tabsElement, fieldset.firstElementChild);

    const langBtns = Array.from(
        tabsElement.querySelectorAll("button[data-lang]")
    );

    langBtns.forEach((btn) => {
        btn.onclick = () => {
            langBtns.forEach((b) => b.classList.remove("selected"));
            btn.classList.add("selected");

            if (btn.dataset.lang != site_language_default_code) {
                rows.forEach((r) => {
                    r.style.display = "none";
                    if (r.dataset.lang == btn.dataset.lang) {
                        r.style.display = "block";
                    }
                });
            } else {
                rows.forEach((r) => {
                    r.style.display = "block";
                    if (r.dataset.lang && r.dataset.lang != btn.dataset.lang) {
                        r.style.display = "none";
                    }
                });
            }
        };
    });

    rows.forEach((r) => {
        r.style.display = "block";
        if (r.dataset.lang && r.dataset.lang != site_language_default_code) {
            r.style.display = "none";
        }
    });
}

document.addEventListener("DOMContentLoaded", function () {
    const site_language_codes = window.site_language_codes;
    const site_language_default_code = window.site_language_default_code;

    const form = document.querySelector("#content-main form[method='post']");

    if (!form) {
        return;
    }

    if (form.id == "changelist-form") {
        return;
    }

    form.classList.add("form-lang");

    const translate_fields = JSON.parse(
        form.querySelector("#id_translate_fields").value
    );

    translate_fields.forEach((fieldname) => {
        let field = form.querySelector(`.form-row.field-${fieldname}`);

        field.dataset["lang"] = site_language_default_code;

        site_language_codes.forEach(([lang, _]) => {
            if (lang != site_language_default_code) {
                let field_lang = form.querySelector(
                    `.form-row.field-${fieldname}_${lang}`
                );

                field_lang.dataset["lang"] = lang;
            }
        });
    });

    addLangTabs(form, site_language_default_code, site_language_codes);
});
