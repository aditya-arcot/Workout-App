### base
FROM node:24 AS base

WORKDIR /src

# optimize layer caching
COPY package*.json ./
RUN npm ci

COPY src/ ./src/
COPY index.html tsconfig*.json vite.config.ts ./


### dev
FROM base AS dev

EXPOSE 5173

# binds all interfaces
CMD ["npm", "run", "dev", "--", "--host"]


### build
FROM base AS build

ARG VITE_API_URL
ENV VITE_API_URL=${VITE_API_URL}

RUN npm run build


### prod
FROM nginx:alpine AS prod

COPY --from=build /src/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

CMD ["nginx", "-g", "daemon off;"]
