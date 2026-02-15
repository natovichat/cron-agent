# Clean Logs - לוגים נקיים

תיקייה זו מכילה לוגים נקיים שמראים **רק** את השיחות עם Cursor AI:
- הפרומפט ששלחנו
- התשובה שקיבלנו

**ללא**: debugging, מחשבות פנימיות, או מידע טכני.

## פורמט הלוג

כל קובץ לוג נקרא: `conversation_YYYY-MM-DD.log`

### דוגמת תוכן:

```
======================================================================
[2025-02-15 14:30:00] Task ID: 12345

📤 PROMPT:
שלח מייל ללקוח חשוב עם עדכון על המוצר החדש

📥 RESPONSE:
✉️ נשלח מייל אוטומטי ללקוח

======================================================================

======================================================================
[2025-02-15 14:30:05] Task ID: 12346

📤 PROMPT:
צור דוח שבועי של כל המכירות

📥 RESPONSE:
📊 נוצר דוח מפורט ונשלח למייל

======================================================================
```

## שימוש

הלוגים הנקיים מושלמים ל:
- 📊 ניתוח שיחות עם ה-AI
- 📈 מעקב אחר ביצועים
- 🔍 סקירה מהירה של פעילות
- 📝 תיעוד להצגה למנהלים/לקוחות
- 🎓 למידה והשבחה של פרומפטים

## הבדל מהלוג הרגיל

| לוג רגיל | לוג נקי |
|----------|---------|
| כולל debugging | רק שיחות |
| הודעות טכניות | פורמט נקי |
| שגיאות מפורטות | תוצאות בלבד |
| Stack traces | מסקנות |
| זמני הרצה מדויקים | תאריך שעה פשוט |

## גישה ללוגים

הלוגים נוצרים אוטומטית כאשר Cron Agent רץ.

כדי לראות את הלוג האחרון:
```bash
# Linux/Mac
tail -f clean_logs/conversation_$(date +%Y-%m-%d).log

# או פשוט
cat clean_logs/conversation_*.log | tail -20
```

## ניקוי

לוגים ישנים לא נמחקים אוטומטית. כדי לנקות:

```bash
# מחיקת לוגים מלפני 30 יום
find clean_logs/ -name "conversation_*.log" -mtime +30 -delete

# שמירת רק 10 הלוגים האחרונים
ls -t clean_logs/conversation_*.log | tail -n +11 | xargs rm -f
```

## הגדרות

ניתן לשנות את מיקום התיקייה ב-`cron_agent.py`:

```python
agent = CronAgent(
    todoist_token=token,
    clean_log_dir="my_custom_logs"  # תיקייה מותאמת אישית
)
```
