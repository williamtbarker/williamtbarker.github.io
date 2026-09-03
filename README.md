# williamtbarker.github.io

Static source for the professional portfolio of Will Barker, PhD.

## Local preview

```bash
python3 -m http.server 8000
```

Open <http://localhost:8000> and stop the server with `Control-C`.

## Checks

```bash
python3 scripts/check_site.py
git diff --check
```

The site is dependency-free and deployed from the repository root through GitHub Pages.
