# nginx/Dockerfile
FROM nginx:1.25-alpine

# Borra la configuración por defecto
RUN rm /etc/nginx/conf.d/default.conf

# Copia nuestra configuración personalizada
COPY default.conf /etc/nginx/conf.d/

EXPOSE 80