#!/bin/bash
GREEN="\033[32m"
RED="\033[31m"
RESET="\033[0m"

# Function to kill all background processes on exit
cleanup() {
    echo -e "\n${RED}Stopping all services...${RESET}"
    pm2 stop ecu-backend 2>/dev/null
    exit
}

# Trap Ctrl+C (SIGINT) and call cleanup
trap cleanup SIGINT

# Kill any existing processes to prevent conflicts
echo "Cleaning up ports/processes..."
pkill -f "node server.js" 2>/dev/null

# Start Database Service
echo "Checking MySQL Service..."
sudo systemctl start mysql

echo "Starting Backend Server with PM2..."
# Use ecosystem.config.js for production-grade management
pm2 start ecosystem.config.js --env production
BACKEND_PID=$(pm2 jlist | jq -r '.[] | select(.name=="ecu-backend") | .pid')
echo -e "Backend managed by PM2"
cd ..

# Wait for backend to initialize
sleep 3

IP=$(hostname -I | awk '{print $1}')
echo -e "\n${GREEN}Application Started!${RESET}"
echo -e "Admin Dashboard: http://$IP:3000/"
echo -e "Login Page:      http://$IP:3000/login.html"
echo -e "Logs:            backend.log"
echo "Services are running in background. Press Ctrl+C to stop."

# Wait indefinitely for PM2 processes
pm2 logs ecu-backend
