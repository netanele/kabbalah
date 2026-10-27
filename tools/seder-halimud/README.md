# tools/seder-halimud – בניית הנתונים של דף "סדר הלימוד"

| קובץ | מה הוא |
|---|---|
| `videos.json` | כל סרטוני הערוץ של הרב תורג'מן (העלאות, שידורים חיים, קצרים, הערוץ הישן) עם הפלייליסטים. הורד ב-27.10.2026 עם yt-dlp (`--flat-playlist -J` על `/videos`, `/streams`, `/shorts` וכל פלייליסט). להוספת סרטונים חדשים: להוריד מחדש ולמזג, או להוסיף רשומה ידנית |
| `curate.py` | שיבוץ כל סרטון למדרגה, לבלוק ולסדר (חובה/העשרה). מריצים `python3 -I curate.py` → `video-assign.json`. סרטון שלא שובץ ידנית נופל ל"חכמי המערב, הילולות וסיפורי צדיקים" במדרגה 0 |
| `stages.py` | התוכן הכתוב ביד: תשע המדרגות, יחידות הדף/התרגול/הספר, השערים, הסכנות, ורשימת הספרים (`BOOKS`) |
| `drive-books.json` | מלאי תיקיית הספרים בדרייב (Torah/Books), כל קובץ עם מזהה ונתיב |
| `book-drive-map.json` | איזה קובץ בדרייב שייך לאיזה ספר (מפתח ב-`stages.BOOKS` → רשימת מזהים) |
| `build_data.py` | בונה את `js/seder-halimud-data.js` (המדרגות, היחידות, הקטלוג) ואת `js/books.js` (הספרים). מריצים `python3 -I tools/seder-halimud/build_data.py` מתיקיית הפרויקט |

סדר עדכון: `videos.json` → `curate.py` → `stages.py` / `book-drive-map.json` → `build_data.py`.
