FROM nginx:alpine

COPY nginx.conf /etc/nginx/nginx.conf

# Remove default html files
RUN rm -rf /usr/share/nginx/html/*

# Copy built files
COPY dist/ /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
