#!/bin/bash
# Setup script for Cron Agent
# סקריפט התקנה אוטומטי

echo "🚀 התקנת Cron Agent"
echo "===================="
echo ""

# בדיקת Python
echo "📋 בודק התקנת Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 לא מותקן!"
    echo "התקן Python 3.8+ מ: https://www.python.org/downloads/"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d ' ' -f 2)
echo "✅ Python $PYTHON_VERSION מותקן"
echo ""

# יצירת virtual environment
echo "📦 יוצר virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Virtual environment נוצר"
else
    echo "⚠️  Virtual environment כבר קיים"
fi
echo ""

# הפעלת virtual environment
echo "🔧 מפעיל virtual environment..."
source venv/bin/activate
echo "✅ Virtual environment פעיל"
echo ""

# התקנת תלויות
echo "📥 מתקין תלויות..."
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt
echo "✅ כל התלויות הותקנו"
echo ""

# יצירת קובץ .env
if [ ! -f ".env" ]; then
    echo "📝 יוצר קובץ .env..."
    cp .env.example .env
    echo "✅ קובץ .env נוצר"
    echo ""
    echo "⚠️  חשוב! ערוך את קובץ .env והוסף את ה-TODOIST_TOKEN שלך"
    echo "   קבל Token מ: https://todoist.com/app/settings/integrations/developer"
else
    echo "⚠️  קובץ .env כבר קיים"
fi
echo ""

# הצגת הוראות סיום
echo "✅ ההתקנה הושלמה בהצלחה!"
echo ""
echo "📋 צעדים הבאים:"
echo "   1. ערוך את קובץ .env והוסף את ה-TODOIST_TOKEN"
echo "   2. הפעל את המערכת: python cron_agent.py"
echo ""
echo "📚 למידע נוסף: cat README.md"
echo ""
echo "🎉 בהצלחה!"
