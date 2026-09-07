# מערכת ניהול דיווחי נזק — Building Real-World Systems

מטלת סיום לקורס **From Code to Real Systems / חשיבה ארכיטקטונית**.

המערכת נבנתה באופן מצטבר לאורך שלוש הסדנאות ומרכזת את כל הדרישות שלהן:

| סדנה | נושא | מה נוסף |
|------|------|---------|
| סדנה 1 — Emergency MVP | Building the Foundation | ישות `DamageReport`, שלושה מסכים, CRUD בסיסי, סטטוסים `NEW` / `IN_REVIEW`, ובחלק ב' — `WAITING_FOR_VALIDATION` |
| סדנה 2 — Growing Complexity | Managing Complexity | שדות תמונות/דו"ח מהנדס/בדיקת זכאות/מספר דירות/אישור חברתי, חיווי "ניתן להתחיל שיקום", עמודת "ממתין בתור לעבודה" + פילטר, כפתור "פתח בקשת תקציב" עם אכיפת חוקים, אישור חברתי למבנים מעל 24 דירות, עמודת/פילטר "מוכן לפתיחת תקציב" |
| סדנה 3 — Crisis Load | Designing for Scale | סטטוסים `BUILDING_IN_RESTORATION` / `RESTORATION_COMPLETED`, יכולת **הפקת תיק אכלוס מחדש** — שירות נפרד + `POST /buildings/{id}/return-home-package` שמפיק PDF רשמי בעברית (RTL) |

## סטאק

- **Backend:** Python 3.14 + FastAPI, אחסון In-Memory (כפי שהמטלה מתירה)
- **PDF:** `fpdf2` + עיצוב טקסט של HarfBuzz לתמיכת RTL, גופן Noto Sans Hebrew (OFL)
- **Frontend:** דף HTML/JS יחיד (Vanilla), מוגש על ידי אותו שרת

## הרצה

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate        # Windows  (source .venv/bin/activate ב-macOS/Linux)
pip install -r requirements.txt
python run.py
```

פותחים את הדפדפן בכתובת <http://localhost:8000> .
תיעוד ה-API האינטראקטיבי זמין ב-<http://localhost:8000/docs> .

בהפעלה נטענים נתוני דוגמה שמכסים את כל תרחישי הקצה (מבנה שמוכן לתקציב, מבנה גדול ללא אישור חברתי, מבנה ששוקם במלואו וזכאי לתיק אכלוס וכו').

## ארכיטקטורה — היכן נמצא כל חוק עסקי

הלוגיקה העסקית מרוכזת בשירותים; ה-Routers וה-PDF לא משכפלים חוקים.

```
backend/app/
├── main.py                         הרכבת האפליקציה, הגשת PDFים והפרונט
├── domain.py                       סטטוסים, תוויות, סף אישור חברתי (24)
├── repository.py                   מאגר In-Memory + נתוני seed
├── schemas.py                      מודלי קלט (Pydantic)
├── serialize.py                    הוספת חיוויים מחושבים לתגובת ה-API
├── routers/
│   ├── reports.py                  /reports   (סדנה 1–2)
│   └── buildings.py                /buildings/{id}/return-home-package (סדנה 3)
└── services/
    ├── rehabilitation_service.py   "ניתן להתחיל שיקום", "ממתין בתור לעבודה", "מוכן לתקציב"
    ├── budget_service.py           זכאות לפתיחת בקשת תקציב + כלל האישור החברתי
    └── occupation_file_service.py  זכאות + אורקסטרציה של הפקת תיק אכלוס מחדש
        └── pdf/occupation_pdf.py   רינדור ה-PDF הרשמי (עברית, RTL)
```

### חוקים עסקיים מרכזיים

- **ניתן להתחיל שיקום** — קיימות תמונות נזק **וגם** דו"ח מהנדס **וגם** בדיקת זכאות.
- **ממתין בתור לעבודה** — קיים דו"ח מהנדס **וגם** בדיקת זכאות.
- **פתיחת בקשת תקציב** — שלושת מסמכי הבסיס, ובנוסף: מבנה מעל 24 דירות מחייב אישור חברתי.
- **הפקת תיק אכלוס מחדש** — דו"ח מהנדס **וגם** בדיקת זכאות **וגם** בקשת תקציב פתוחה **וגם** סטטוס `RESTORATION_COMPLETED`.

## API

| Method | Path | תיאור |
|--------|------|-------|
| `GET` | `/reports` | רשימת דיווחים. פילטרים: `?workQueue=true`, `?budgetReady=true` |
| `POST` | `/reports` | יצירת דיווח (נוצר בסטטוס `WAITING_FOR_VALIDATION`) |
| `GET` | `/reports/{id}` | פרטי דיווח + כל החיוויים |
| `PATCH` | `/reports/{id}/status` | עדכון סטטוס |
| `PATCH` | `/reports/{id}/details` | עדכון תמונות/דו"ח/זכאות/מספר דירות/אישור חברתי |
| `GET` | `/reports/{id}/budget-eligibility` | בדיקת זכאות לתקציב |
| `POST` | `/reports/{id}/budget-request` | פתיחת בקשת תקציב (403 כשלא זכאי) |
| `GET` | `/buildings/{id}/occupation-eligibility` | בדיקת זכאות לתיק אכלוס מחדש |
| `POST` | `/buildings/{id}/return-home-package` | הפקת ה-PDF. מחזיר `{ "fileUrl": "..." }` |

## בדיקות

```bash
cd backend
pip install pytest
python -m pytest
```

הבדיקות מכסות את חוקי הזכאות, זרימת פתיחת בקשת התקציב, וזכאות/הפקה של תיק אכלוס מחדש.
