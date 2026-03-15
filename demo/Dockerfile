FROM nginx:alpine

LABEL maintainer="agentic-skills"
LABEL description="Reveal.js presentation for Agentic Skills Platform"

# Copy presentation files
COPY index.html /usr/share/nginx/html/index.html

# Nginx config for SPA
RUN echo 'server { \
    listen 80; \
    server_name _; \
    root /usr/share/nginx/html; \
    index index.html; \
    location / { \
        try_files $uri $uri/ /index.html; \
    } \
}' > /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
