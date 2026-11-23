FROM mcr.microsoft.com/playwright:v1.38.1-jammy

ENV CI=true HUSKY=0
ARG T0_COMMIT=25bc8a514eb8b080a4ed23959ac4229f18cb3cff

WORKDIR /app
COPY . .

RUN git config --global --add safe.directory /app && \
    git checkout -f "$T0_COMMIT" && \
    yarn install --frozen-lockfile && \
    yarn lerna run build

CMD ["sleep", "infinity"]

