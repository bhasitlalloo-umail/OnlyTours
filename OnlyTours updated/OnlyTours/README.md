# OnlyTours

This is a repository for the project OnlyTours, created and managed by the group OnlyWebs.

## Fixed since the last version

- **Images/CSS missing on `/attractions/` and `/customer-registration/`.**
  The cause was `STATIC_URL = 'static/'` (no leading slash) in
  `settings.py`. `{% static %}` produced a *relative* URL, so on the
  root page (`/`) it resolved fine, but on any nested page it resolved
  relative to that page's own path (e.g. `/attractions/static/...`)
  instead of `/static/...`, which 404s. Every image, every stylesheet,
  and the pill-shaped "rectangle" input styling and dropdown chevrons
  all disappeared as a result. Fixed by setting `STATIC_URL = '/static/'`.
- **Each page really does have its own URL** — this was already true
  in the project structure (see the table below); if it looked like
  one page with everything crammed in, that was the separate, single-file
  *preview* artifact from before (built only so you could eyeball
  responsiveness without running the server) — not this actual Django
  project. Run `python manage.py runserver` and visit each URL below
  and you'll get a distinct page per URL, with the browser address bar
  changing each time.
- Customer registration's fields were already real, working
  `<input>`/`<select>` elements you can click into and type — that
  didn't change, it just wasn't visible while the CSS/images were 404ing.

## Running it

```bash
python -m venv venv
source venv/bin/activate      # venv\Scripts\activate on Windows
pip install django
python manage.py migrate
python manage.py runserver
```

Then visit `http://127.0.0.1:8000/`.

## Pages / URLs

| URL                              | Name (`OnlyToursApp:<name>`) | Template                     |
|-----------------------------------|-------------------------------|-------------------------------|
| `/`                                | `home`                        | `home.html`                   |
| `/register/`                      | `register`                    | `register.html`               |
| `/customer-registration/`         | `customerReg`                 | `customerReg.html`            |
| `/attractions/`                   | `attractions`                 | `attractions.html`            |
| `/tour-guide-registration/`       | `tourGuideReg`                | `coming_soon.html` (stub)     |
| `/book-now/`                      | `book_now`                    | `coming_soon.html` (stub)     |
| `/tour-guide/`                    | `tour_guide`                  | `coming_soon.html` (stub)     |
| `/login/`                         | `log_in`                      | `coming_soon.html` (stub)     |
| `/admin/`                         | Django admin                  | —                              |

The four "stub" pages don't have real designs yet — they render a
shared `coming_soon.html` placeholder (with a link back home) so every
link on the site resolves instead of 404ing. Swap each one out for a
real view + template as it's designed; nothing else needs to change.

## What changed when converting from the raw Figma export

- **Made it a real, connected Django app.** Added `OnlyTours/settings.py`,
  project-level `urls.py`, `wsgi.py`/`asgi.py`, and wired every nav
  link / button in every template to a named URL via `{% url %}` —
  including the ones that only had a bare `href` on a `<div>` before
  (browsers ignore `href` on non-`<a>` elements, so those were dead).
- **Fully responsive CSS.** The original stylesheets positioned every
  element with absolute pixel coordinates on a fixed canvas (e.g.
  `2586×1969px`), so it only ever looked right at one screen size.
  Every page has been rebuilt with flexbox/grid, `clamp()` for fluid
  type and spacing, and a mobile breakpoint, so it reflows correctly
  from a phone up through a wide desktop monitor. Shared variables and
  the nav live in `static/OnlyToursApp/css/base.css`; each page has
  its own small stylesheet for its specific layout.
- **Real form fields.** `customerReg.html` now uses actual
  `<input>`/`<select>` elements (with a `<form>`, CSRF token, and
  `required` attributes) instead of empty decorative rectangles.
- **Fixed static file paths** to match Django's app-static convention
  (`static/OnlyToursApp/...`) and pointed every template at the right
  one.
- **Added a `home.html` landing page** since "Home" was linked from
  the attractions nav but didn't exist yet.
- **Placeholder images** for the four attraction photos and the two
  dropdown-chevron icons that were referenced in the CSS/HTML but not
  included in the upload — generated so nothing 404s, styled to match
  the brand colors. Swap the files in
  `static/OnlyToursApp/images/attractions/` for real photos whenever
  you have them (same filenames, so nothing else needs to change).
- **Fonts:** the export specified two custom fonts
  ("SwankyAndMooMoo-Regular" and "Inter") that weren't part of the
  upload, so `base.css` currently falls back to system fonts. Drop the
  real font files into a `static/OnlyToursApp/fonts/` folder and add
  `@font-face` rules in `base.css` to restore the exact look.
- `Desktop.html` from the upload was the raw, non-templated Figma
  export of the customer registration screen — `customerReg.html`
  already covers that page as a real Django template, so it wasn't
  carried over.
