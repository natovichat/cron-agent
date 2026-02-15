# Cron Agent - אוטומציה חכמה לניהול משימות

![Python](https://img.shields.io/badge/Python-3.8+-blue)
![License](https://img.shields.io/badge/License-MIT-green)

## 📖 תיאור

**Cron Agent** היא מערכת אוטומטית שמשלבת בין אפליקציית ניהול משימות (Todoist), סוכן AI חכם (Cursor), ומתזמן משימות (Cron) כדי ליצור פתרון אוטומציה מתקדם.

המערכת רצה כל 5 שניות, קוראת משימות חדשות מ-Todoist, שולחת אותן ל-Cursor AI לביצוע, ומעדכנת את התוצאות בחזרה.

### 🎯 יתרונות

- ⏰ **אוטומציה מלאה** - אין צורך לזכור לבדוק משימות
- 🤖 **AI חכם** - Cursor מבצע משימות מורכבות
- ⚡ **תגובה מהירה** - עיבוד כל 5 שניות
- 📊 **מעקב מרכזי** - כל המשימות במקום אחד
- 🔄 **עדכונים אוטומטיים** - תיעוד וסטטוס בזמן אמת

## 🏗️ ארכיטקטורה

```
┌──────────────┐
│   Todoist    │  ← משימות נוספות על ידי המשתמש
│   (משימות)   │
└──────┬───────┘
       │ API Call
       │ (כל 5 שניות)
       ▼
┌──────────────┐
│  Cron Agent  │  ← Python Script
│   (מתזמן)    │
└──────┬───────┘
       │ Send Tasks
       ▼
┌──────────────┐
│  Cursor AI   │  ← מבצע משימות
│   (מבצע)     │
└──────┬───────┘
       │ Results
       ▼
┌──────────────┐
│   Update     │  ← עדכון אוטומטי
│   Todoist    │
└──────────────┘
```

## 🚀 התקנה מהירה

### דרישות מקדימות

- Python 3.8 ומעלה
- חשבון Todoist (חינמי או Pro)
- Cursor AI (אופציונלי לשלב זה)

### שלב 1: שכפול הפרויקט

```bash
git clone https://github.com/yourusername/cron-agent.git
cd cron-agent
```

### שלב 2: התקנת תלויות

```bash
pip install -r requirements.txt
```

### שלב 3: קבלת API Token מ-Todoist

1. היכנס ל-[Todoist Settings](https://todoist.com/app/settings/integrations/developer)
2. העתק את ה-API Token שלך
3. שמור אותו במקום בטוח

### שלב 4: הגדרת Token

#### Linux/Mac:
```bash
export TODOIST_TOKEN='your-api-token-here'
```

#### Windows (PowerShell):
```powershell
$env:TODOIST_TOKEN='your-api-token-here'
```

#### או צור קובץ `.env`:
```bash
echo "TODOIST_TOKEN=your-api-token-here" > .env
```

### שלב 5: הרצה

```bash
python cron_agent.py
```

## 📋 שימוש

### הוספת משימה ב-Todoist

1. פתח את Todoist (Web/Mobile/Desktop)
2. הוסף משימה חדשה, למשל:
   - "שלח מייל ללקוח חשוב"
   - "צור דוח שבועי"
   - "עדכן מסד נתונים"

### המערכת תטפל בזה אוטומטית

תוך 5 שניות:
1. ✅ המערכת תזהה את המשימה
2. 🤖 Cursor AI יבצע אותה
3. 📝 התוצאות יעודכנו ב-Todoist
4. ✔️ המשימה תסומן כהושלמה

### דוגמת פלט

```
==================================================
⏰ 2025-02-15 14:30:00
==================================================
📋 נמצאו 3 משימות פעילות

📝 מעבד משימה: שלח מייל ללקוח #12345
🤖 Cursor AI מעבד: שלח מייל ללקוח #12345
✅ המשימה הושלמה בהצלחה

📝 מעבד משימה: צור דוח שבועי
🤖 Cursor AI מעבד: צור דוח שבועי
✅ המשימה הושלמה בהצלחה

--------------------------------------------------
📊 סטטיסטיקות:
   🎯 סה"כ משימות: 2
   ✅ הצליחו: 2
   ❌ נכשלו: 0
   ⏱️  זמן פעילות: 0:02:30
--------------------------------------------------
```

## ⚙️ הגדרות מתקדמות

### שינוי מרווח זמן

ערוך את `cron_agent.py` ושנה את המרווח:

```python
# במקום 5 שניות
agent.start(interval_seconds=5)

# לדוגמה, כל 30 שניות
agent.start(interval_seconds=30)

# או כל דקה
agent.start(interval_seconds=60)
```

### הפעלה רק עבור פרויקט מסוים

הוסף סינון לפי פרויקט:

```python
def get_tasks(self, project_id: Optional[str] = None):
    params = {}
    if project_id:
        params['project_id'] = project_id
    
    response = requests.get(
        f"{self.base_url}/tasks",
        headers=self.headers,
        params=params
    )
    # ...
```

### הפעלה כ-Service (Linux)

צור קובץ `cron-agent.service`:

```ini
[Unit]
Description=Cron Agent - Todoist Automation
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/path/to/cron-agent
Environment="TODOIST_TOKEN=your-token"
ExecStart=/usr/bin/python3 /path/to/cron-agent/cron_agent.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

הפעל:
```bash
sudo cp cron-agent.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable cron-agent
sudo systemctl start cron-agent
```

## 🔧 פיתוח והרחבה

### הוספת אינטגרציה חדשה

#### דוגמה: שליחת מיילים דרך Gmail

```python
import smtplib
from email.mime.text import MIMEText

class EmailService:
    def __init__(self, email: str, password: str):
        self.email = email
        self.password = password
    
    def send_email(self, to: str, subject: str, body: str):
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = self.email
        msg['To'] = to
        
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(self.email, self.password)
            smtp.send_message(msg)

# שימוש ב-CursorAgent
class CursorAgent:
    def __init__(self):
        self.email_service = EmailService(
            os.getenv('GMAIL_EMAIL'),
            os.getenv('GMAIL_PASSWORD')
        )
    
    def _analyze_and_execute(self, content: str) -> str:
        if "שלח מייל" in content:
            # נתח את הפרטים מה-content
            to, subject, body = self._parse_email_request(content)
            self.email_service.send_email(to, subject, body)
            return f"✉️ מייל נשלח ל-{to}"
```

### הוספת לוגים מתקדמים

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('cron_agent.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('CronAgent')
```

## 🔒 אבטחה

### שמירה על ה-Token

❌ **לעולם אל תכניס את ה-Token לקוד!**

✅ השתמש ב-environment variables או `.env`:
```bash
# .env
TODOIST_TOKEN=your-secret-token-here
```

✅ הוסף `.env` ל-`.gitignore`:
```bash
echo ".env" >> .gitignore
```

### הרשאות קבצים

```bash
# הגבל גישה לקובץ .env
chmod 600 .env

# הגבל גישה לקובץ הקונפיגורציה
chmod 600 config.json
```

## 📊 מעקב וניטור

### לוגים נקיים (Clean Logs)

המערכת יוצרת **שני סוגי לוגים**:

#### 1. לוג רגיל (Console)
כל הפעילות נרשמת בקונסול כולל debugging, שגיאות, וסטטיסטיקות.

```bash
python cron_agent.py >> cron_agent.log 2>&1
```

#### 2. לוג נקי (Clean Logs) ⭐ חדש!
לוג מיוחד שמראה **רק** את השיחות עם Cursor AI:
- 📤 הפרומפט ששלחת
- 📥 התשובה שקיבלת
- ❌ **בלי** debugging, מחשבות, או שגיאות

**מיקום:** `clean_logs/conversation_YYYY-MM-DD.log`

**דוגמת תוכן:**
```
======================================================================
[2025-02-15 14:30:00] Task ID: 12345

📤 PROMPT:
שלח מייל ללקוח חשוב

📥 RESPONSE:
✉️ נשלח מייל אוטומטי ללקוח

======================================================================
```

**צפייה בלוג הנקי:**
```bash
# הצג את הלוג של היום
cat clean_logs/conversation_$(date +%Y-%m-%d).log

# מעקב חי
tail -f clean_logs/conversation_$(date +%Y-%m-%d).log
```

**למה זה שימושי?**
- 📊 ניתוח שיחות מול AI
- 📈 מעקב אחר איכות תשובות
- 🎓 למידה והשבחת פרומפטים
- 📝 תיעוד להצגה (בלי טכניקליות)
- 🔍 סקירה מהירה של פעילות

### סטטיסטיקות

המערכת מציגה סטטיסטיקות בזמן אמת:
- סך משימות שעובדו
- משימות שהצליחו
- משימות שנכשלו
- זמן פעילות

## 🐛 פתרון בעיות

### הסקריפט לא מוצא משימות

**בעיה:** "📋 נמצאו 0 משימות פעילות"

**פתרון:**
1. ודא שיש משימות פתוחות ב-Todoist
2. בדוק שה-Token תקין
3. ודא שהמשימות לא סומנו כהושלמו

### שגיאת Authentication

**בעיה:** "401 Unauthorized"

**פתרון:**
1. בדוק שה-TODOIST_TOKEN מוגדר נכון
2. העתק Token חדש מ-Todoist Settings
3. ודא שאין רווחים בהתחלה/סוף ה-Token

### המערכת לא מתעדכנת

**בעיה:** משימות לא מתעדכנות ב-Todoist

**פתרון:**
1. בדוק חיבור אינטרנט
2. ודא שה-API של Todoist זמין
3. בדוק את הלוגים לשגיאות

## 🤝 תרומה לפרויקט

נשמח לקבל תרומות! אפשר:
- 🐛 לדווח על באגים
- 💡 להציע פיצ'רים חדשים
- 📝 לשפר תיעוד
- 🔧 להוסיף קוד

### תהליך:
1. Fork את הפרויקט
2. צור branch חדש (`git checkout -b feature/amazing-feature`)
3. Commit את השינויים (`git commit -m 'Add amazing feature'`)
4. Push ל-branch (`git push origin feature/amazing-feature`)
5. פתח Pull Request

## 📝 רישיון

פרויקט זה מופץ תחת רישיון MIT. ראה `LICENSE` לפרטים.

## 🙏 תודות

- [Todoist](https://todoist.com) - אפליקציית ניהול משימות מעולה
- [Cursor](https://cursor.sh) - עורך קוד חכם עם AI
- [Schedule](https://schedule.readthedocs.io/) - ספריית תזמון פשוטה וחכמה

## 📧 יצירת קשר

- 📧 Email: your.email@example.com
- 🐦 Twitter: [@yourhandle](https://twitter.com/yourhandle)
- 💼 LinkedIn: [Your Name](https://linkedin.com/in/yourname)

## 🗺️ מפת דרכים

- [ ] תמיכה באפליקציות משימות נוספות (Asana, Trello)
- [ ] ממשק Web לניהול
- [ ] תמיכה במשימות מקבילות
- [ ] אינטגרציה מלאה עם Cursor API
- [ ] דשבורד ניטור בזמן אמת
- [ ] תמיכה ב-webhooks
- [ ] מצב dry-run לבדיקות

---

**נבנה עם ❤️ על ידי [שמך]**

⭐ אם אהבת את הפרויקט, תן לנו כוכב ב-GitHub!
