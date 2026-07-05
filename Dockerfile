FROM node:24-bookworm-slim AS base

ENV PNPM_HOME="/pnpm"
ENV PATH="$PNPM_HOME:$PATH"
RUN corepack enable

WORKDIR /app

# ---

FROM base AS deps

COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
RUN --mount=type=cache,id=pnpm-store,target=/pnpm/store pnpm install --frozen-lockfile

# ---

FROM deps AS build

ARG EMDASH_DB=postgres
ENV EMDASH_DB=$EMDASH_DB

COPY . .
RUN pnpm build
RUN pnpm prune --prod

# ---

FROM node:24-bookworm-slim AS runtime

WORKDIR /app

ENV NODE_ENV=production
ENV HOST=0.0.0.0
ENV PORT=4321
ENV EMDASH_DATA_DIR=/data
ENV EMDASH_DB=postgres

RUN useradd -m -u 10001 appuser

COPY --from=build /app/dist ./dist
COPY --from=build /app/node_modules ./node_modules
COPY --from=build /app/package.json ./package.json
COPY --from=build /app/seed ./seed
COPY --from=build /app/scripts ./scripts

COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh && chown -R appuser:appuser /app /entrypoint.sh

USER appuser

EXPOSE 4321

ENTRYPOINT ["/entrypoint.sh"]
CMD ["node", "./dist/server/entry.mjs"]
