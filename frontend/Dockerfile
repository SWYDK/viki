# Dockerfile для фронтенда (React)
FROM nginx:alpine

# Копируем файлы сборки React
COPY build/ /usr/share/nginx/html

# Экспортируем порт 80 для Nginx
EXPOSE 80

# Запуск Nginx
CMD ["nginx", "-g", "daemon off;"]
