#!/bin/bash
# View Clean Logs Script

CLEAN_LOGS_DIR="clean_logs"
TODAY=$(date +%Y-%m-%d)
TODAY_LOG="${CLEAN_LOGS_DIR}/conversation_${TODAY}.log"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}📝 Clean Logs Viewer${NC}"
echo -e "${BLUE}===================${NC}"
echo ""

# Check if directory exists
if [ ! -d "$CLEAN_LOGS_DIR" ]; then
    echo -e "${YELLOW}⚠️  Directory does not exist: $CLEAN_LOGS_DIR${NC}"
    exit 1
fi

# Count files
LOG_COUNT=$(ls -1 ${CLEAN_LOGS_DIR}/conversation_*.log 2>/dev/null | wc -l)

if [ $LOG_COUNT -eq 0 ]; then
    echo -e "${YELLOW}⚠️  No log files found${NC}"
    exit 1
fi

echo -e "${GREEN}Found $LOG_COUNT log files${NC}"
echo ""

# Menu
echo "Choose an option:"
echo "1. View today's log"
echo "2. View all logs"
echo "3. View last 10 conversations"
echo "4. Search in logs"
echo "5. Live tail (follow)"
echo "6. View example"
echo ""
read -p "Your choice (1-6): " choice

case $choice in
    1)
        echo -e "\n${BLUE}=== Today's Log ===${NC}\n"
        if [ -f "$TODAY_LOG" ]; then
            cat "$TODAY_LOG"
        else
            echo -e "${YELLOW}⚠️  No log for today${NC}"
        fi
        ;;
    2)
        echo -e "\n${BLUE}=== All Logs ===${NC}\n"
        for log in ${CLEAN_LOGS_DIR}/conversation_*.log; do
            echo -e "${GREEN}📁 $(basename $log)${NC}"
            cat "$log"
            echo ""
        done
        ;;
    3)
        echo -e "\n${BLUE}=== Last 10 Conversations ===${NC}\n"
        cat ${CLEAN_LOGS_DIR}/conversation_*.log | grep -A 8 "^=====" | tail -80
        ;;
    4)
        read -p "Enter search term: " search_term
        echo -e "\n${BLUE}=== Search Results: '$search_term' ===${NC}\n"
        grep -i -A 8 "$search_term" ${CLEAN_LOGS_DIR}/conversation_*.log
        ;;
    5)
        if [ -f "$TODAY_LOG" ]; then
            echo -e "\n${BLUE}=== Live Tail (Press Ctrl+C to stop) ===${NC}\n"
            tail -f "$TODAY_LOG"
        else
            echo -e "${YELLOW}⚠️  No log for today${NC}"
        fi
        ;;
    6)
        echo -e "\n${BLUE}=== Example Log ===${NC}\n"
        if [ -f "${CLEAN_LOGS_DIR}/conversation_example.log" ]; then
            cat "${CLEAN_LOGS_DIR}/conversation_example.log"
        else
            echo -e "${YELLOW}⚠️  Example file does not exist${NC}"
        fi
        ;;
    *)
        echo -e "${YELLOW}Invalid choice${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}✅ Done${NC}"
