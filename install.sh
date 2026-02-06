#!/bin/bash

# Network Devices Monitoring Dashboard - Deployment Script

# 0. Set Project Root (Handle running from deployment/ or root)
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$SCRIPT_DIR"

cd "$PROJECT_ROOT" || { echo "Error: Could not find project root"; exit 1; }

RESET="\033[0m"
BOLD="\033[1m"
RED="\033[31m"
GREEN="\033[32m"
YELLOW="\033[33m"
CYAN="\033[36m"
BLUE="\033[34m"

info() { echo -e "${BLUE}[INFO]${RESET} $1"; }
success() { echo -e "${GREEN}[SUCCESS]${RESET} $1"; }
warn() { echo -e "${YELLOW}[WARNING]${RESET} $1"; }
error() { echo -e "${RED}[ERROR]${RESET} $1"; exit 1; }

check_command() {
    if ! command -v "$1" &> /dev/null; then
        warn "$1 is not installed."
        return 1
    fi
    return 0
}

# 1. Update and Install System Dependencies
info "Updating package lists and checking dependencies..."
if check_command node; then
    success "Node.js is installed."
else
    info "Installing Node.js..."
    curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
    sudo apt-get install -y nodejs
fi

if check_command mysql; then
    success "MySQL Client is installed."
else
    info "Installing MySQL..."
    sudo apt-get install -y mysql-server
    # Ensure MySQL service is started
    sudo systemctl start mysql
    sudo systemctl enable mysql
fi

# 2. Interactive Configuration
echo -e "\n${BOLD}${CYAN}=== System Configuration ===${RESET}"

# Password
while true; do
    read -sp "Enter Admin Password: " ADMIN_PASS
    echo
    read -sp "Confirm Password: " ADMIN_PASS_CONFIRM
    echo
    if [ "$ADMIN_PASS" == "$ADMIN_PASS_CONFIRM" ] && [ -n "$ADMIN_PASS" ]; then
        break
    else
        echo -e "${RED}Passwords do not match or are empty. Try again.${RESET}"
    fi
done

# Database Password (New)
echo -e "\n${YELLOW}Database Configuration:${RESET}"
read -sp "Enter MySQL Root Password (leave empty if none): " DB_ROOT_PASS
echo ""

# Security Questions - REMOVED
# QUESTIONS=(...)
# select_question() ...

echo ""
info "Configuration captured."

# 3. Setup Database
info "Setting up Database..."
DB_NAME="ecu_application" 
DB_USER="root"

# Check .env
ENV_FILE="backend/.env"

if [ -f "$ENV_FILE" ]; then
    cp "$ENV_FILE" "$ENV_FILE.bak"
    info "Backed up existing .env to .env.bak"
fi

info "Creating backend/.env file..."
cat <<EOT > "$ENV_FILE"
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=$DB_ROOT_PASS
DB_NAME=$DB_NAME
PORT=3000
SESSION_SECRET=$(openssl rand -hex 32)
EOT

# Create Database if not exists
# We will use the python/sequelize sync to create tables, but we need the DB itself.
SQL_CREATE_DB="CREATE DATABASE IF NOT EXISTS $DB_NAME;"

if [ -n "$DB_ROOT_PASS" ]; then
    sudo mysql -u root -p"$DB_ROOT_PASS" -e "$SQL_CREATE_DB" || error "Failed to create database. Check credentials."
else
    # Try with sudo if plain connect fails, as root often uses socket auth on Ubuntu
    if ! mysql -u root -e "$SQL_CREATE_DB" 2>/dev/null; then
         sudo mysql -e "$SQL_CREATE_DB" || error "Failed to create database."
    fi
fi

success "Database verified/created."

# 4. Seed Database with User Config
info "Seeding Admin User..."
export ADMIN_USER="admin"
export ADMIN_PASSWORD="$ADMIN_PASS"

# Load .env variables for the seed script
export DB_HOST=localhost
export DB_USER=root
export DB_PASSWORD="$DB_ROOT_PASS"
export DB_NAME="$DB_NAME"

cd backend
info "Installing backend dependencies..."
npm install

info "Running seed script..."
node seedAdmin.js || error "Failed to seed database."
success "Database Seeded with Admin User."

cd ..

# 5. Finalize
success "Installation Complete!"
echo -e "${BOLD}${GREEN}To start the server:${RESET}"
echo -e "  cd backend"
echo -e "  node server.js"
