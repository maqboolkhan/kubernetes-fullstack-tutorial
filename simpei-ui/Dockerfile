# Multi-stage build for Vue.js application
FROM node:18-alpine AS builder

ARG VUE_APP_API_URL=/api
ARG VUE_APP_TITLE="Simpei Todo App"

ENV VUE_APP_API_URL=$VUE_APP_API_URL
ENV VUE_APP_TITLE=$VUE_APP_TITLE

WORKDIR /app
COPY package*.json ./
RUN npm ci

# Copy source code
COPY . .
RUN npm run build

# Production stage with nginx
FROM nginx:alpine


 # use image from build stage
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf.template /etc/nginx/templates/default.conf.template

# Enviroment variables required for nginx (see nginx.conf.template)
ENV BACKEND_HOST=simpei-api
ENV BACKEND_PORT=8000

# Create directories and set permissions
RUN mkdir -p /var/cache/nginx/client_temp && \
    mkdir -p /var/cache/nginx/proxy_temp && \
    mkdir -p /var/cache/nginx/fastcgi_temp && \
    mkdir -p /var/cache/nginx/uwsgi_temp && \
    mkdir -p /var/cache/nginx/scgi_temp && \
    chown -R nginx:nginx /var/cache/nginx && \
    chown -R nginx:nginx /usr/share/nginx/html && \
    chown -R nginx:nginx /etc/nginx/conf.d && \
    touch /var/run/nginx.pid && \
    chown nginx:nginx /var/run/nginx.pid

USER nginx
EXPOSE 3000
CMD ["nginx", "-g", "daemon off;"]