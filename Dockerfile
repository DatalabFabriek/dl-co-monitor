FROM python:latest

# Image labels
ARG IMAGE_CREATED
ARG GIT_DIGEST

LABEL org.opencontainers.image.created=$IMAGE_CREATED
LABEL org.opencontainers.image.revision=$GIT_DIGEST
LABEL org.opencontainers.image.version="0.1.0"
LABEL org.opencontainers.image.authors="harmen@datalab.nl,Denny Zhang"
LABEL org.opencontainers.image.vendor="DatalabFabriek B.V."
LABEL org.opencontainers.image.title="Datalab Studio Docker Service Monitor"

###
# Environmental variables
ENV CHECK_INTERVAL "300"
ENV STARTUP_DELAY "300"
ENV SLACK_WEBHOOK ""
ENV WHITE_LIST ""
ENV MSG_PREFIX ""

###
# Copy & install stuff
USER root
RUN mkdir /datalab
COPY bin/ /datalab/
RUN pip install -r /datalab/requirements.txt
RUN chmod o+x /datalab/*.sh

###
# Entrypoint
ENTRYPOINT ["/datalab/monitor-docker-slack.sh"]
