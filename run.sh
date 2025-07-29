#!/bin/bash

# KDP Global Contract Brokerage System - Development Startup Script

echo "🚀 Starting KDP Global Contract Brokerage System..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check prerequisites
echo -e "${BLUE}Checking prerequisites...${NC}"

if ! command_exists python3; then
    echo -e "${RED}❌ Python 3 is not installed${NC}"
    exit 1
fi

if ! command_exists node; then
    echo -e "${RED}❌ Node.js is not installed${NC}"
    exit 1
fi

if ! command_exists psql; then
    echo -e "${YELLOW}⚠️  PostgreSQL client not found. Make sure PostgreSQL is installed.${NC}"
fi

if ! command_exists redis-cli; then
    echo -e "${YELLOW}⚠️  Redis client not found. Make sure Redis is installed.${NC}"
fi

echo -e "${GREEN}✅ Prerequisites check completed${NC}"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo -e "${YELLOW}📝 Creating .env file from template...${NC}"
    cp .env.example .env
    echo -e "${YELLOW}⚠️  Please edit .env file with your configuration before continuing${NC}"
    read -p "Press Enter to continue after editing .env file..."
fi

# Setup Python virtual environment
if [ ! -d "venv" ]; then
    echo -e "${BLUE}🐍 Creating Python virtual environment...${NC}"
    python3 -m venv venv
fi

echo -e "${BLUE}📦 Activating virtual environment and installing Python dependencies...${NC}"
source venv/bin/activate
pip install -r requirements.txt

# Setup Node.js dependencies
echo -e "${BLUE}📦 Installing Node.js dependencies...${NC}"
npm install

# Check if database exists and create if needed
echo -e "${BLUE}🗄️  Setting up database...${NC}"
source .env
DB_NAME=$(echo $DATABASE_URL | sed 's/.*\/\([^?]*\).*/\1/')

# Create database if it doesn't exist
if command_exists createdb; then
    createdb $DB_NAME 2>/dev/null || echo "Database $DB_NAME already exists or couldn't be created"
fi

# Run database migrations (if using Alembic)
if [ -f "backend/alembic.ini" ]; then
    echo -e "${BLUE}🔄 Running database migrations...${NC}"
    cd backend
    alembic upgrade head
    cd ..
fi

# Function to start a service in background
start_service() {
    local service_name=$1
    local command=$2
    local log_file="logs/${service_name}.log"
    
    mkdir -p logs
    echo -e "${BLUE}🚀 Starting ${service_name}...${NC}"
    eval "$command" > "$log_file" 2>&1 &
    local pid=$!
    echo $pid > "logs/${service_name}.pid"
    echo -e "${GREEN}✅ ${service_name} started (PID: $pid)${NC}"
}

# Start Redis if not running
if ! pgrep redis-server > /dev/null; then
    if command_exists redis-server; then
        start_service "redis" "redis-server"
        sleep 2
    else
        echo -e "${RED}❌ Redis server not found. Please install and start Redis manually.${NC}"
    fi
fi

# Start backend services
echo -e "${BLUE}🖥️  Starting backend services...${NC}"
source venv/bin/activate

# Start FastAPI backend
start_service "backend" "cd backend && python main.py"
sleep 3

# Start Celery worker
start_service "celery-worker" "cd backend && celery -A tasks worker --loglevel=info"
sleep 2

# Start Celery beat scheduler
start_service "celery-beat" "cd backend && celery -A tasks beat --loglevel=info"
sleep 2

# Start React frontend
echo -e "${BLUE}⚛️  Starting React frontend...${NC}"
start_service "frontend" "npm start"

# Wait for services to start
echo -e "${YELLOW}⏳ Waiting for services to initialize...${NC}"
sleep 5

# Check service status
echo -e "${BLUE}📊 Service Status:${NC}"
echo "=================================="

check_service() {
    local service_name=$1
    local pid_file="logs/${service_name}.pid"
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if ps -p $pid > /dev/null; then
            echo -e "${GREEN}✅ ${service_name}: Running (PID: $pid)${NC}"
        else
            echo -e "${RED}❌ ${service_name}: Not running${NC}"
        fi
    else
        echo -e "${RED}❌ ${service_name}: PID file not found${NC}"
    fi
}

check_service "redis"
check_service "backend"
check_service "celery-worker"
check_service "celery-beat"
check_service "frontend"

echo "=================================="
echo -e "${GREEN}🎉 KDP Global Contract Brokerage System is starting up!${NC}"
echo ""
echo -e "${BLUE}📱 Application URLs:${NC}"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo -e "${BLUE}📝 Log files are available in the 'logs' directory${NC}"
echo ""
echo -e "${YELLOW}💡 To stop all services, run: ./stop.sh${NC}"
echo ""

# Create stop script
cat > stop.sh << 'EOF'
#!/bin/bash

echo "🛑 Stopping KDP Global Contract Brokerage System..."

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

stop_service() {
    local service_name=$1
    local pid_file="logs/${service_name}.pid"
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if ps -p $pid > /dev/null; then
            echo -e "${YELLOW}Stopping ${service_name} (PID: $pid)...${NC}"
            kill $pid
            rm "$pid_file"
            echo -e "${GREEN}✅ ${service_name} stopped${NC}"
        else
            echo -e "${RED}❌ ${service_name} was not running${NC}"
            rm "$pid_file" 2>/dev/null
        fi
    else
        echo -e "${RED}❌ ${service_name}: PID file not found${NC}"
    fi
}

stop_service "frontend"
stop_service "celery-beat"
stop_service "celery-worker"
stop_service "backend"
stop_service "redis"

echo -e "${GREEN}🎉 All services stopped${NC}"
EOF

chmod +x stop.sh

echo -e "${GREEN}✨ Setup complete! The system is now running.${NC}"