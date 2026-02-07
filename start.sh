#!/bin/bash
GREEN="\033[32m"
RED="\033[31m"
RESET="\033[0m"

# Function to kill all background processes on exit
cleanup() {
    echo -e "\n${RED}Stopping all services...${RESET}"
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
    fi
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

echo "Starting Backend Server..."
cd backend
# Use nohup to run in background, but we want to see output if possible.
# Using & to run in background and capture PID
node server.js > ../backend.log 2>&1 &
BACKEND_PID=$!
echo -e "Backend running (PID: $BACKEND_PID)"
cd ..

# Wait for backend to initialize
sleep 3

IP=$(hostname -I | awk '{print $1}')
echo -e "\n${GREEN}Application Started!${RESET}"
echo -e "Admin Dashboard: http://$IP:3000/"
echo -e "Login Page:      http://$IP:3000/login.html"
echo -e "Logs:            backend.log"
echo "Services are running in background. Press Ctrl+C to stop."

# Wait indefinitely
wait $BACKEND_PID
