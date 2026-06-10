#
FROM library/python:3.14-slim

RUN apt update

ENV DEBUG=TRUE
ENV PYTHONPATH=/app/

# install nginx
RUN apt-get install nginx vim curl -y --no-install-recommends
# for compiling cryptography module
# RUN apt-get install build-essential libssl-dev libffi-dev python3-dev cargo pkg-config -y --no-install-recommends

# create the folder and the root CA
RUN mkdir -p /app
COPY start-server.sh /app/start-server.sh
RUN chmod +x /app/start-server.sh
COPY requirements.txt /app/requirements.txt
#COPY ../ofxtools/nginx.default /app/

WORKDIR /app
RUN python3 -m venv venv
RUN /app/venv/bin/pip install wheel
RUN /app/venv/bin/pip install -r requirements.txt --retries 60

# copy app
COPY app/app /app/app
COPY app/static /app/static
COPY app/ui /app/ui
COPY app/manage.py /app/manage.py
COPY app/gunicorn.conf.py /app/gunicorn.conf.py
RUN mkdir /app/db
RUN mkdir /app/log

WORKDIR /app/

COPY nginx.default /etc/nginx/sites-available/default
RUN ln -sf /dev/stdout /var/log/nginx/access.log \
    && ln -sf /dev/stderr /var/log/nginx/error.log

HEALTHCHECK --interval=30s --timeout=3s \
  CMD curl -f http://127.0.0.1:8000/ -H 'User-Agent: healthcheck' || exit 1

EXPOSE 8000
STOPSIGNAL SIGTERM
CMD ["/app/start-server.sh"]
