#!/bin/bash

if ! curl -sf http://localhost:8080/count > /dev/null 2>&1; then
    echo "Server not running — starting it now..."
    /app/server &
    sleep 2
fi

uv run pytest /tests/test_outputs.py -v
PYTEST_EXIT=$?

mkdir -p /logs/verifier
if [ $PYTEST_EXIT -eq 0 ]; then
    echo 1 > /logs/verifier/reward.txt
else
    echo 0 > /logs/verifier/reward.txt
fi

exit $PYTEST_EXIT
