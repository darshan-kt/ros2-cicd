FROM nginx:alpine

COPY frontend/ /usr/share/nginx/html/

COPY docker/print_url.sh /docker-entrypoint.d/99-print-url.sh

RUN chmod +x /docker-entrypoint.d/99-print-url.sh