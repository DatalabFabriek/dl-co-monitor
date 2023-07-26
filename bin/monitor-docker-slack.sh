#!/bin/bash
TZ='Europe/Amsterdam'

echo -e "[$(date +'%Y-%m-%d %H:%M:%S.%N')]\tStarting Docker Services monitor..."

if [ -f /run/secrets/dl-co-monitor-slack-webhook ]; then
       export SLACK_WEBHOOK=$(cat /run/secrets/dl-co-monitor-slack-webhook)
fi

if [ ${STARTUP_DELAY:=0} -gt 0 ]; then
       echo -e "[$(date +'%Y-%m-%d %H:%M:%S.%N')]\tEntering start-up delay mode for $STARTUP_DELAY seconds..."
       sleep $STARTUP_DELAY
fi

echo -e "[$(date +'%Y-%m-%d %H:%M:%S.%N')]\tStarting monitoring script..."

python /datalab/monitor-docker-slack.py  --check_interval "$CHECK_INTERVAL" \
       --slack_webhook "$SLACK_WEBHOOK" --whitelist "$WHITE_LIST" \
       --msg_prefix "$MSG_PREFIX"

echo -e "[$(date +'%Y-%m-%d %H:%M:%S.%N')]\tDocker Services monitor stopped"

## File : monitor-docker-slack.sh ends