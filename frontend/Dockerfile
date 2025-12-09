FROM node:22-slim AS build
ARG DEBUG_BUILD=false
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN DEBUG_BUILD=$DEBUG_BUILD npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80

