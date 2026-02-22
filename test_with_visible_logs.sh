#!/bin/bash

echo "Starting server..."
uvicorn api.main:app --port 8000 > /tmp/server.log 2>&1 &
SERVER_PID=$!

echo "Waiting for server to start..."
sleep 15

echo "Checking if server is ready..."
until curl -s http://localhost:8000/health > /dev/null 2>&1; do
    echo "  Waiting for server..."
    sleep 2
done
echo "  Server is ready!"

echo "Running test..."
python test_backend_ba_generation.py

echo ""
echo "======================================================================"
echo "SERVER LOGS:"
echo "======================================================================"
cat /tmp/server.log

echo ""
echo "Killing server..."
kill $SERVER_PID
wait $SERVER_PID 2>/dev/null

echo "Done"
