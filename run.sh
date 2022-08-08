#!/bin/bash

if [ -z $1 ]; then
    PORT=8081
else
   PORT=$1
fi
export PORT=$PORT
echo "Starting server on port $PORT"
Python3 api.py