# [שם הפרויקט שלך]

מערכת Backend מבוססת FastAPI לניהול משתמשים מאובטח, הכוללת אימות JWT, אינטגרציה עם Redis לניהול סשנים, ובסיס נתונים PostgreSQL.

## 📂 מבנה הפרויקט
הפרויקט מאורגן בצורה מודולרית להבטחת תחזוקה נוחה:
* `app/`
    * `db/`: חיבורים למסד הנתונים ומודלים (`database.py`, `db_models.py`).
    * `helpers/`: פונקציות עזר, כלים לאבטחה (`security.py`, `utils.py`).
    * `middlewares/`: שכבות הגנה ואימות (`auth_middleware.py`).
    * `routes/`: נקודות הקצה של ה-API (`auth.py`, `users.py`).
    * `schemas/`: הגדרות Pydantic לולידציה של נתונים (`auth_schemas.py`, `users_schemas.py`).
    * `services/`: לוגיקה עסקית (`redis_service.py`).
* `config.py`: ניהול הגדרות המערכת באמצעות `Pydantic Settings`.
* `docker-compose.yml`: הגדרת סביבת ההרצה (Docker).

---

## 🛠 הוראות הרצה

### 1. דרישות קדם
ודא שמותקנים אצלך:
* [Docker](https://www.docker.com/)
* [Docker Compose](https://docs.docker.com/)

### 2. הגדרת סביבה
העתק את קובץ הדוגמה וצור את קובץ הקונפיגורציה שלך:
```bash
cp .env.example .env