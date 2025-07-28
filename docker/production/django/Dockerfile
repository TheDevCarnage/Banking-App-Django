FROM docker.io/python:3.12.2-slim-bookworm AS python

# Stage 1: Build our dependency wheels
FROM python AS python-build-stage

ARG BUILD_ENVIRONMENT=production

RUN apt-get update && apt-get install --no-install-recommends -y \
    build-essential \
    libpq-dev

COPY ./requirements .

RUN pip wheel --wheel-dir /usr/src/app/wheels \
    -r ${BUILD_ENVIRONMENT}.txt

# Stage 2 : Run Stage
FROM python AS python-run-stage

ARG BUILD_ENVIRONMENT=production

ARG APP_HOME=/app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    BUILD_ENV=${BUILD_ENVIRONMENT}

WORKDIR ${APP_HOME}

RUN apt-get update && apt-get install --no-install-recommends -y \
    sudo git bash-completion nano ssh \
    libpq-dev gettext \
    && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
    && rm -rf /var/lib/apt/lists/*

RUN addgroup --system django && \
    adduser --system --ingroup django django && \
    mkdir -p ${APP_HOME}/staticfiles && \
    chown -R django:django ${APP_HOME}/staticfiles && \
    chmod -R 775 ${APP_HOME}/staticfiles

COPY --from=python-build-stage /usr/src/app/wheels /wheels/

RUN pip install --no-cache-dir --no-index --find-links=/wheels/ /wheels/* \
    && rm -rf /wheels/

COPY --chown=django:django ./docker/production/django/entrypoint.sh /entrypoint.sh
COPY --chown=django:django ./docker/production/django/start.sh /start.sh
COPY --chown=django:django ./docker/production/django/celery/worker/start.sh /start-celeryworker.sh
COPY --chown=django:django ./docker/production/django/celery/beat/start.sh /start-celerybeat.sh
COPY --chown=django:django ./docker/production/django/celery/flower/start.sh /start-flower.sh

RUN sed -i 's/\r$//g' /entrypoint.sh /start.sh /start-celeryworker.sh /start-celerybeat.sh \
    /start-flower.sh && \
    chmod +x /entrypoint.sh /start.sh /start-celeryworker.sh /start-celerybeat.sh /start-flower.sh

RUN mkdir -p /app/logs && \
    chown -R django:django /app/logs && \
    chmod 775 /app/logs

COPY --chown=django:django . ${APP_HOME}

USER django

ENTRYPOINT ["/entrypoint.sh"]
