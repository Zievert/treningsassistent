#!/bin/bash
# Setup SSH tunnel for Postgres MCP server
# Run this script before starting Claude Code

echo "Setting up SSH tunnel for Postgres MCP server..."

# Kill existing tunnel if it exists
pkill -f "ssh -f -N -L 15432:localhost:5432 gull" 2>/dev/null

sleep 1

# Create Postgres tunnel (port 15432)
echo "Creating Postgres tunnel (localhost:15432 -> gull:5432)..."
ssh -f -N -L 15432:localhost:5432 gull
if [ $? -eq 0 ]; then
  echo "✓ Postgres tunnel created"
else
  echo "✗ Failed to create Postgres tunnel"
  exit 1
fi

sleep 1

# Verify tunnel is listening
echo ""
echo "Verifying tunnel..."
if ss -tuln | grep -q ":15432.*LISTEN"; then
  echo "✓ Postgres tunnel listening on port 15432"
else
  echo "✗ Postgres tunnel not listening"
fi

# Test Postgres connection
echo ""
echo "Testing connection..."
if psql "postgres://postgres:Tr3n1ng_Pr0d_P4ssw0rd_2024!@localhost:15432/treningsassistent" -c "SELECT 1" &>/dev/null; then
  echo "✓ Postgres connection successful"
else
  echo "✗ Postgres connection failed"
fi

# Verify FastAPI direct connection (no tunnel needed)
echo ""
echo "Verifying FastAPI direct connection..."
if curl -s -m 5 http://10.0.0.20:8000/health &>/dev/null; then
  echo "✓ FastAPI direct connection successful (no tunnel needed)"
else
  echo "✗ FastAPI connection failed"
fi

echo ""
echo "SSH tunnel is ready! You can now start Claude Code."
echo ""
echo "Note: FastAPI connects directly to 10.0.0.20:8000 (no tunnel needed)"
echo ""
echo "To check tunnel status later, run:"
echo "  ps aux | grep 'ssh -f -N'"
echo "  ss -tuln | grep 15432"
