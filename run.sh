#!/bin/bash
CORES_COUNT=$(grep -c ^processor /proc/cpuinfo)
WORKERS_COUNT=${WORKERS_COUNT:-$((CORES_COUNT + 1))}

WEB_SERVER=${WEB_SERVER:-"granian"}

if [ "$WEB_SERVER" == "granian" ]; then
  echo 1
  exec granian --interface asgi --workers "${WORKERS_COUNT}" --host 0.0.0.0 --port 8000 "app.__main__:fastapi_app" --respawn-failed-workers
elif [ "$WEB_SERVER" == "gunicorn" ]; then
  echo 2
  exec gunicorn --bind 0.0.0.0:8000 --workers "${WORKERS_COUNT}" --worker-class uvicorn.workers.UvicornWorker "app.__main__:fastapi_app"
fi
