# frontend/Dockerfile
FROM nginx:alpine

# Копируем готовую сборку React в директорию Nginx
COPY . /usr/share/nginx/html

# Настраиваем Nginx для обслуживания React-приложения
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
