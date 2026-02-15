# הוראות הגדרה - Cron Agent

## ✅ מה נעשה עד עכשיו

1. **ניקינו את המערכת הישנה:**
   - ✅ עצרנו את LaunchAgent הישן
   - ✅ מחקנו את `com.cursor.agent.taskrunner.plist`
   - ✅ ניקינו את כל ה-cronjobs
   - ✅ הרגנו תהליכים ישנים

2. **הגדרנו את המערכת החדשה:**
   - ✅ יצרנו LaunchAgent חדש: `com.cursor.cronagent.plist`
   - ✅ יצרנו סקריפט wrapper: `run_cron_agent.sh`
   - ✅ יצרנו virtual environment והתקנו תלויות
   - ✅ יצרנו קובץ `.env` מהדוגמה
   - ✅ טענו את ה-LaunchAgent החדש

## ⚠️ צעד אחד נותר - הגדרת TODOIST_TOKEN

כדי שהסוכן יעבוד, צריך להגדיר את ה-Todoist API Token:

### שלב 1: קבלת Token מ-Todoist

1. היכנס ל-[Todoist Settings](https://todoist.com/app/settings/integrations/developer)
2. העתק את ה-**API Token** שלך
3. שמור אותו במקום בטוח

### שלב 2: עדכון קובץ .env

ערוך את הקובץ:
```bash
nano "/Users/aviad.natovich/personal/cron agent/.env"
```

או:
```bash
open -e "/Users/aviad.natovich/personal/cron agent/.env"
```

החלף את:
```
TODOIST_TOKEN=your-todoist-api-token-here
```

עם ה-Token שקיבלת:
```
TODOIST_TOKEN=abc123xyz789yourrealtokenhere
```

שמור את הקובץ.

### שלב 3: הפעלה מחדש

```bash
# עצור את הסוכן הנוכחי
launchctl unload ~/Library/LaunchAgents/com.cursor.cronagent.plist

# טען אותו שוב עם ה-Token החדש
launchctl load ~/Library/LaunchAgents/com.cursor.cronagent.plist
```

## 📊 בדיקת סטטוס

### בדוק אם הסוכן רץ:
```bash
launchctl list | grep cursor
```

פלט תקין:
```
PID     STATUS  LABEL
53360   0       com.cursor.cronagent
```

### צפה בלוגים:
```bash
# לוג רגיל
tail -f "/Users/aviad.natovich/personal/cron agent/logs/cron_agent.log"

# לוג שגיאות
tail -f "/Users/aviad.natovich/personal/cron agent/logs/cron_agent_error.log"

# לוג נקי (רק שיחות עם AI)
tail -f "/Users/aviad.natovich/personal/cron agent/clean_logs/conversation_$(date +%Y-%m-%d).log"
```

### בדוק תהליכים:
```bash
ps aux | grep cron_agent | grep -v grep
```

## 🎯 מה הסוכן עושה?

הסוכן:
1. רץ **כל הזמן** ברקע (`KeepAlive: true`)
2. בודק משימות ב-Todoist **כל 5 שניות**
3. מבצע משימות באמצעות Cursor AI (סימולציה)
4. מעדכן את הסטטוס ב-Todoist
5. שומר לוגים נקיים של כל שיחה

## 🛠️ פקודות שימושיות

### עצירת הסוכן:
```bash
launchctl unload ~/Library/LaunchAgents/com.cursor.cronagent.plist
```

### הפעלת הסוכן:
```bash
launchctl load ~/Library/LaunchAgents/com.cursor.cronagent.plist
```

### הרצה ידנית (לבדיקה):
```bash
cd "/Users/aviad.natovich/personal/cron agent"
./run_cron_agent.sh
```

### הרצה עם debugging:
```bash
cd "/Users/aviad.natovich/personal/cron agent"
source venv/bin/activate
export TODOIST_TOKEN="your-token-here"
python cron_agent.py
```

## 📁 קבצים חשובים

```
~/personal/cron agent/
├── cron_agent.py              # הקוד הראשי
├── run_cron_agent.sh          # wrapper script
├── .env                       # הגדרות (כולל TOKEN)
├── venv/                      # virtual environment
├── logs/                      # לוגים רגילים
├── clean_logs/                # לוגים נקיים
└── ~/Library/LaunchAgents/
    └── com.cursor.cronagent.plist  # הגדרת LaunchAgent
```

## ⚡ Quick Start

```bash
# 1. הגדר TOKEN
echo 'TODOIST_TOKEN=YOUR_REAL_TOKEN_HERE' > "/Users/aviad.natovich/personal/cron agent/.env.local"

# 2. הפעל את הסוכן
launchctl unload ~/Library/LaunchAgents/com.cursor.cronagent.plist
launchctl load ~/Library/LaunchAgents/com.cursor.cronagent.plist

# 3. צפה בלוגים
tail -f "/Users/aviad.natovich/personal/cron agent/logs/cron_agent.log"
```

## 🐛 פתרון בעיות

### הסוכן לא רץ (STATUS != 0)

בדוק לוגים:
```bash
tail -20 "/Users/aviad.natovich/personal/cron agent/logs/cron_agent_error.log"
```

### "TODOIST_TOKEN לא הוגדר"

ודא ש-.env מכיל TOKEN תקין:
```bash
cat "/Users/aviad.natovich/personal/cron agent/.env" | grep TODOIST_TOKEN
```

### "ModuleNotFoundError"

התקן מחדש תלויות:
```bash
cd "/Users/aviad.natovich/personal/cron agent"
./venv/bin/pip install -r requirements.txt
```

### הסוכן רץ אבל לא מוצא משימות

1. ודא שיש משימות פתוחות ב-Todoist
2. ודא שה-TOKEN תקין
3. בדוק את הלוגים

## 🎉 הצלחה!

אם הכל עובד, תראה:
- ✅ PID בפלט של `launchctl list`
- ✅ STATUS = 0
- ✅ משימות מתבצעות ב-Todoist
- ✅ לוגים נקיים נוצרים

---

**צריך עזרה?** בדוק את הלוגים או הרץ את הסוכן ידנית עם debugging.
