#!/bin/bash -ex

if [[ -f /run/secrets/dl-co-monitor-slack-webhook ]] && [[ "$SLACK_WEBHOOK" == ""]]; then
       export SLACK_WEBHOOK=$(cat /run/secrets/dl-co-monitor-slack-webhook)
fi

if [$STARTUP_DELAY -gt 0]; then
       echo "Entering start-up delay mode for $STARTUP_DELAY seconds..."
       sleep $STARTUP_DELAY
fi

python /datalab/monitor-docker-slack.py  --check_interval "$CHECK_INTERVAL" \
       --slack_webhook "$SLACK_WEBHOOK" --whitelist "$WHITE_LIST" \
       --msg_prefix "$MSG_PREFIX"

## File : monitor-docker-slack.sh ends