FROM node:16.18-alpine as deps

WORKDIR /app

COPY . .

RUN yarn install

FROM node:16.18-alpine as build

WORKDIR /app

COPY --from=deps /app/package.json .
COPY --from=deps /app/node_modules ./node_modules
COPY --from=deps /app/src ./src
COPY --from=deps /app/static ./static
COPY --from=deps /app/vite.config.ts .
COPY --from=deps /app/svelte.config.js .
COPY --from=deps /app/.env .

RUN yarn build

FROM node:16.18-alpine as run

WORKDIR /app

COPY --from=build /app/package.json .
COPY --from=build /app/build ./build
COPY --from=build /app/static ./static

# TODO: production
COPY --from=build /app/.svelte-kit ./.svelte-kit
COPY --from=build /app/vite.config.ts ./vite.config.ts
COPY --from=build /app/svelte.config.js ./svelte.config.js
COPY --from=build /app/node_modules ./node_modules

EXPOSE 8080

CMD ["node_modules/.bin/vite", "preview", "--host", "--port", "8080"]