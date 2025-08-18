#!/bin/bash

# Symplifika Django Server Startup Script

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting Symplifika Django Server...${NC}"

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo -e "${YELLOW}Activating virtual environment...${NC}"
    source venv/bin/activate
else
    echo -e "${YELLOW}No virtual environment found. Using system Python...${NC}"
fi

# Check if Django is installed
python -c "import django" 2>/dev/null
if [ $? -ne 0 ]; then
    echo -e "${RED}Django not found. Installing requirements...${NC}"
    pip install -r requirements.txt
fi

# Run database migrations
echo -e "${YELLOW}Running database migrations...${NC}"
python manage.py migrate

# Check for any issues
echo -e "${YELLOW}Running system checks...${NC}"
python manage.py check

# Collect static files (if needed)
echo -e "${YELLOW}Collecting static files...${NC}"
python manage.py collectstatic --noinput

# Start the server
echo -e "${GREEN}Starting Django development server on http://127.0.0.1:8000${NC}"
echo -e "${YELLOW}Press CTRL+C to stop the server${NC}"
python manage.py runserver 127.0.0.1:8000
