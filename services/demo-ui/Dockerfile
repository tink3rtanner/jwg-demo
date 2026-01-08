FROM nginx:alpine

COPY services/demo-ui/*.html /usr/share/nginx/html/
COPY services/demo-ui/*.js /usr/share/nginx/html/
COPY services/demo-ui/*.css /usr/share/nginx/html/

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
