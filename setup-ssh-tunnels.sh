#!/bin/bash
# Setup SSH tunnels for MCP servers (Postgres and FastAPI)
# Run this script before starting Claude Code

echo "========================================"
echo "Setting up SSH tunnels for MCP servers"
echo "========================================"

# Kill existing tunnels if they exist
echo ""
echo "Killing existing tunnels..."
pkill -f "ssh -f -N -L 15432:localhost:5432 gull" 2>/dev/null
pkill -f "ssh -f -N -L 8000:localhost:8000 gull" 2>/dev/null
sleep 1

# Create Postgres tunnel (port 15432)
echo ""
echo "Creating Postgres tunnel (localhost:15432 -> gull:5432)..."
ssh -f -N -L 15432:localhost:5432 gull
if [ $? -eq 0 ]; then
  echo "✓ Postgres tunnel created"
else
  echo "✗ Failed to create Postgres tunnel"
  exit 1
fi

sleep 1

# Create FastAPI tunnel (port 8000)
echo ""
echo "Creating FastAPI tunnel (localhost:8000 -> gull:8000)..."
ssh -f -N -L 8000:localhost:8000 gull
if [ $? -eq 0 ]; then
  echo "✓ FastAPI tunnel created"
else
  echo "✗ Failed to create FastAPI tunnel"
  exit 1
fi

sleep 1

# Verify tunnels are listening
echo ""
echo "Verifying tunnels..."
if ss -tuln | grep -q ":15432.*LISTEN"; then
  echo "✓ Postgres tunnel listening on port 15432"
else
  echo "✗ Postgres tunnel not listening"
fi

if ss -tuln | grep -q ":8000.*LISTEN"; then
  echo "✓ FastAPI tunnel listening on port 8000"
else
  echo "✗ FastAPI tunnel not listening"
fi

# Test connections
echo ""
echo "Testing connections..."
if timeout 3 curl -s http://localhost:8000/health &>/dev/null; then
  echo "✓ FastAPI connection successful"
else
  echo "✗ FastAPI connection failed"
fi

echo ""
echo "========================================"
echo "✓ SSH tunnels are ready!"
echo "========================================"
echo ""
echo "Active tunnels:"
echo "  - Postgres: localhost:15432 -> gull:5432"
echo "  - FastAPI:  localhost:8000 -> gull:8000"
echo ""
echo "You can now start Claude Code."
echo ""
echo "To check tunnel status later, run:"
echo "  ps aux | grep 'ssh -f -N'"
echo "  ss -tuln | grep -E '15432|8000'"
