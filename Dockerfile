FROM python:3.12.1-bookworm

WORKDIR /app
ENV FLASK_APP=application:create_app()

RUN curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg \
    && echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_21.x nodistro main" | tee /etc/apt/sources.list.d/nodesource.list

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        nginx \
        nodejs \
        postgresql-client-common \
        postgresql-client-15 \
        supervisor \
        tox \
    && apt-get clean \
    && rm -Rf /var/lib/apt/lists/*

RUN git clone https://github.com/shouldbee/reserved-usernames.git /tmp/reserved-usernames

COPY ./app/package.json ./app/yarn.lock ./app/application/ui/static/* /static/
RUN corepack enable && (cd /static && yarn install)

COPY ./app/requirements.txt /tmp/
RUN pip install --upgrade pip && pip install -r /tmp/requirements.txt

COPY ./app /app

RUN ln -s /app/entrypoint.sh / \
    && ln -s /app/nginx.conf /etc/nginx/conf.d/ \
    && ln -s /app/supervisord.conf /etc/supervisor/conf.d/ \
    && ln -s /app/gunicorn.py /etc/

ENTRYPOINT [ "/entrypoint.sh" ]
