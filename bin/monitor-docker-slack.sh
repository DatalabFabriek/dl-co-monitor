#!/bin/bash

echo -e "[$(TZ='Europe/Amsterdam' date +'%Y-%m-%d %H:%M:%S.%N')]\tStarting Docker Services monitor..."

if [ -f /run/secrets/dl-co-monitor-slack-webhook ]; then
       export SLACK_WEBHOOK=$(cat /run/secrets/dl-co-monitor-slack-webhook)
fi

if [ ${STARTUP_DELAY:=0} -gt 0 ]; then
       echo -e "[$(TZ='Europe/Amsterdam' date +'%Y-%m-%d %H:%M:%S.%N')]\tEntering start-up delay mode for $STARTUP_DELAY seconds..."
       sleep $STARTUP_DELAY
fi

echo -e "[$(TZ='Europe/Amsterdam' date +'%Y-%m-%d %H:%M:%S.%N')]\tStarting monitoring script..."

python /datalab/monitor-docker-slack.py  --check_interval "$CHECK_INTERVAL" \
       --slack_webhook "$SLACK_WEBHOOK" --whitelist "$WHITE_LIST" \
       --msg_prefix "$MSG_PREFIX"

msg_end="[$(TZ='Europe/Amsterdam' date +'%Y-%m-%d %H:%M:%S.%N')]\tDocker Services monitor Python script stopped; normally it will start up again automatically. If it doesn't, please check."
echo -e $msg_end

curl -X POST -H 'Content-type: application/json' --data "{\"text\":\"$msg_end\"}" "$SLACK_WEBHOOK"

## File : monitor-docker-slack.sh ends