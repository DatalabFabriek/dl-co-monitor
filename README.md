# Docker Service monitoring
This Docker image allows you to monitor Docker services (rather than Docker containers, as is the case with [the repository this is a fork of](https://www.github.com/dennyzhang/monitor-docker-slack)).

It does so by checking the `Docker service ls` command and comparing the number of desired containers by the actual number of running containers. For example, the command `docker service ls` will output, for each service, 'Replicas = 1/3'. In this case, the service is considered unhealthy because the desired number of replicas (3) is lower than the running number of replicas (1). If this situation is encountered, a message will be posted to Slack listing the service name, the number of replicas and the desired number of replicas.

Keep in mind that there might be valid reasons why the actual and desired number of replicas differ. For example, you might have very short-living containers executing small tasks. Then the Docker service coordinator will have a hard time in keeping the number of running replicas in sync with the desired number of replicas. This monitoring service is not developed for these cases. We're primarily aimed at monitoring services which have relatively long run-time per replica/container. This is the case with most webserver set-ups.

Also note that this monitoring service is not meant for monitoring individual Docker containers. We kindly refer you to the [original repository](https://www.github.com/dennyzhang/monitor-docker-slack) for this purpose.

## Source
This is a fork of the container by [Denny Zhang](https://www.github.com/dennyzhang/monitor-docker-slack). Code is licensed under [MIT License](https://www.dennyzhang.com/wp-content/mit_license.txt).

This repository is highly changed from the original so one could consider this an extensive rework of the original.

## Modifications
This fork includes the [pull request by Svelix](https://github.com/dennyzhang/monitor-docker-slack/pull/7).

It also includes modifications to the file structure of the repository (i.e. moving all code that is copied to the container to the bin/ folder in the repo).

Moreover, hard-coded version requirements for Python dependencies are stripped since some of the dependencies are no longer available.

A GitHub Workflow is added to automate the building of the Docker images.

## How to use
You can run this image as a Docker service or as an standalone Docker container.

Example code for running as a service:
```
docker service create \
  --name dl-co-monitor \
  --with-registry-auth \
  --replicas 1 \
  --restart-max-attempts 600 \
  --restart-delay 60s \
  --restart-condition any \
  --env SLACK_WEBHOOK="https://hooks.slack.com/services/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" \
  --mount type=bind,source=/var/run/docker.sock,target=/var/run/docker.sock \
  ghcr.io/datalabfabriek/dl-co-monitor:main
```