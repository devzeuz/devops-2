#!/bin/sh
# Substitute environment variables into Nginx config
envsubst '$PORT $ACTIVE_POOL' < /etc/nginx/nginx.conf.template > /etc/nginx/nginx.conf
# Start Nginx in foreground
nginx -g 'daemon off;'

