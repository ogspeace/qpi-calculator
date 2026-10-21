# QPI Calculator

A simple Flask web app where students enter their subjects, units and grades,
then press **Calculate** to get their QPI (Quality Point Index).
Styled with Bootstrap 5.3 in a teal theme, with a live Philippine-time
clock in the navbar.

```
QPI = Summation of (quality points × units) ÷ total units
```

The scale and formula follow the Ateneo de Davao University Student Handbook
(2025 edition), Section 15. The QPI is rounded off to four decimal places
(Sec. 15.3). ASF and NSTP are not counted in the QPI (Sec. 17.5), so students
should leave them out.

| Grade | Quality points |
|-------|----------------|
| A     | 4.0            |
| B+    | 3.5            |
| B     | 3.0            |
| C+    | 2.5            |
| C     | 2.0            |
| D     | 1.0            |
| F     | 0.0            |
| FD    | 0.0 (Failure Debarred) |
| WP    | Not counted in QPI (Withdrawn with Permission) |

To change the scale, edit `GRADE_POINTS` in `app.py` (use `None` for a grade that is not counted).

## Run locally

```bash
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py                    # http://127.0.0.1:5000
```

Run the tests:

```bash
pip install -r requirements-dev.txt
pytest
```

## Deploy on PythonAnywhere

1. Open a **Bash console** on PythonAnywhere and clone the repo:
   ```bash
   git clone https://github.com/ogspeace/qpiCalc.git
   cd qpiCalc
   mkvirtualenv qpicalc --python=python3.13
   pip install -r requirements.txt
   ```
2. Go to the **Web** tab → **Add a new web app** → **Manual configuration**
   → pick the same Python version (3.13).
3. Under **Virtualenv**, enter `qpicalc` (or `/home/<username>/.virtualenvs/qpicalc`).
4. Under **Code**, set *Source code* and *Working directory* to
   `/home/<username>/qpiCalc`.
5. Click the **WSGI configuration file** link and replace its contents with:
   ```python
   import sys

   path = "/home/<username>/qpiCalc"
   if path not in sys.path:
       sys.path.insert(0, path)

   from app import app as application
   ```
6. Under **Static files**, add URL `/static/` → directory
   `/home/<username>/qpiCalc/static`.
7. Click **Reload**. The site is live at `https://<username>.pythonanywhere.com`.

To update later: `cd ~/qpiCalc && git pull`, then **Reload** on the Web tab.

## Project structure

```
app.py               Flask app and QPI logic
templates/index.html Page template (Bootstrap 5.3.8 via CDN)
static/css/style.css Teal theme
static/js/app.js     Subject rows, navbar clock, dark mode, right-click block
test_app.py          Tests
```
