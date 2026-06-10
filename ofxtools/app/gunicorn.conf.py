user="www-data"
bind="0.0.0.0:8001"
workers=5
timeout=1200
capture_output=True
loglevel="debug"
accesslog="/app/log/gunicorn_access.log"
errorlog="/app/log/gunicorn_error.log"