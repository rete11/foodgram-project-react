FROM nginx:1.22.1

RUN mkdir -p /usr/share/nginx/html/api/docs

COPY nginx.conf /etc/nginx/templates/default.conf.template

COPY 404.html /usr/share/nginx/html/