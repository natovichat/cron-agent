#!/bin/bash
# סקריפט לצפייה בלוגים הנקיים
# View Clean Logs Script

CLEAN_LOGS_DIR="clean_logs"
TODAY=$(date +%Y-%m-%d)
TODAY_LOG="${CLEAN_LOGS_DIR}/conversation_${TODAY}.log"

# צבעים
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}📝 Clean Logs Viewer${NC}"
echo -e "${BLUE}===================${NC}"
echo ""

# בדיקה אם התיקייה קיימת
if [ ! -d "$CLEAN_LOGS_DIR" ]; then
    echo -e "${YELLOW}⚠️  תיקייה לא קיימת: $CLEAN_LOGS_DIR${NC}"
    exit 1
fi

# ספירת קבצים
LOG_COUNT=$(ls -1 ${CLEAN_LOGS_DIR}/conversation_*.log 2>/dev/null | wc -l)

if [ $LOG_COUNT -eq 0 ]; then
    echo -e "${YELLOW}⚠️  לא נמצאו קבצי לוג${NC}"
    exit 1
fi

echo -e "${GREEN}נמצאו $LOG_COUNT קבצי לוג${NC}"
echo ""

# תפריט
echo "בחר אפשרות:"
echo "1. הצג לוג של היום"
echo "2. הצג את כל הלוגים"
echo "3. הצג 10 השיחות האחרונות"
echo "4. חיפוש בלוגים"
echo "5. מעקב חי (live tail)"
echo "6. צפה בדוגמה"
echo ""
read -p "הבחירה שלך (1-6): " choice

case $choice in
    1)
        echo -e "\n${BLUE}=== לוג של היום ===${NC}\n"
        if [ -f "$TODAY_LOG" ]; then
            cat "$TODAY_LOG"
        else
            echo -e "${YELLOW}⚠️  אין לוג להיום${NC}"
        fi
        ;;
    2)
        echo -e "\n${BLUE}=== כל הלוגים ===${NC}\n"
        for log in ${CLEAN_LOGS_DIR}/conversation_*.log; do
            echo -e "${GREEN}📁 $(basename $log)${NC}"
            cat "$log"
            echo ""
        done
        ;;
    3)
        echo -e "\n${BLUE}=== 10 שיחות אחרונות ===${NC}\n"
        cat ${CLEAN_LOGS_DIR}/conversation_*.log | grep -A 8 "^=====" | tail -80
        ;;
    4)
        read -p "הקלד מילת חיפוש: " search_term
        echo -e "\n${BLUE}=== תוצאות חיפוש: '$search_term' ===${NC}\n"
        grep -i -A 8 "$search_term" ${CLEAN_LOGS_DIR}/conversation_*.log
        ;;
    5)
        if [ -f "$TODAY_LOG" ]; then
            echo -e "\n${BLUE}=== מעקב חי (לחץ Ctrl+C לעצירה) ===${NC}\n"
            tail -f "$TODAY_LOG"
        else
            echo -e "${YELLOW}⚠️  אין לוג להיום${NC}"
        fi
        ;;
    6)
        echo -e "\n${BLUE}=== דוגמת לוג ===${NC}\n"
        if [ -f "${CLEAN_LOGS_DIR}/conversation_example.log" ]; then
            cat "${CLEAN_LOGS_DIR}/conversation_example.log"
        else
            echo -e "${YELLOW}⚠️  קובץ הדוגמה לא קיים${NC}"
        fi
        ;;
    *)
        echo -e "${YELLOW}בחירה לא תקינה${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}✅ סיים${NC}"
