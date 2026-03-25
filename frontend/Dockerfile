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

# Run linting and type checks before build
RUN npm run lint || echo "Linting warnings detected"
RUN npx tsc --noEmit || echo "Type check warnings detected"

# Build the app
RUN npm run build

FROM nginx:alpine

# Copy built app to nginx
COPY --from=build /app/dist /usr/share/nginx/html

# Add health check for nginx
HEALTHCHECK --interval=10s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost:80 || exit 1

EXPOSE 80