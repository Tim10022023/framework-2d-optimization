FROM node:20-alpine AS build

WORKDIR /app

ARG VITE_API_URL=http://localhost:8000
ARG VITE_PUBLIC_APP_URL=http://localhost:5173
ARG VITE_TEACHER_PIN=CHANGE_ME

ENV VITE_API_URL=$VITE_API_URL
ENV VITE_PUBLIC_APP_URL=$VITE_PUBLIC_APP_URL
ENV VITE_TEACHER_PIN=$VITE_TEACHER_PIN

COPY package*.json ./
RUN npm ci --include=dev

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80