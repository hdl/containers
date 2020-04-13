#!/usr/bin/env sh

set -e

if [ -z "$BOT_TOKEN" ]; then
  echo "BOT_TOKEN cannot be empty!"
  exit 1
fi

for etype; do
  curl -X POST https://api.github.com/repos/eine/symbiflow-containers/dispatches \
  -H "Content-Type: application/json" -H 'Accept: application/vnd.github.everest-preview+json' \
  -H "Authorization: token ${BOT_TOKEN}" \
  --data "{\"event_type\": \"$etype\"}"
done
