FROM docker.io/ubuntu:24.04 AS builder

ENV CI=1
ENV DEBIAN_FRONTEND=noninteractive

RUN apt update && apt install -y \
    curl \
    git \
    python3-pip \
    python3-venv \
  && pip3 install --break-system-packages vcstool \
  && curl -fsSL https://get.pnpm.io/install.sh | bash - \
  && rm -rf /var/lib/apt/lists/*

ENV PNPM_HOME=/root/.local/share/pnpm
ENV PATH="$PNPM_HOME:$PATH"

RUN pnpm env use --global lts

WORKDIR /ws

COPY rmf.repos /tmp/rmf.repos
RUN vcs import /ws < /tmp/rmf.repos

RUN cd /ws \
  && pnpm install --filter rmf-dashboard-framework...

RUN mkdir -p /ws/packages/rmf-dashboard-framework/examples/target
COPY dashboard/ /ws/packages/rmf-dashboard-framework/examples/target/

COPY dashboard_resources/ /ws/packages/rmf-dashboard-framework/examples/shared/public/resources/

COPY vite.config.ts /ws/packages/rmf-dashboard-framework/examples/shared/vite.config.ts

RUN cd /ws/packages/rmf-dashboard-framework \
  && pnpm run build:example examples/target


FROM docker.io/nginx:stable

COPY --from=builder --chown=root:nginx \
  /ws/packages/rmf-dashboard-framework/examples/target/dist \
  /usr/share/nginx/html

COPY nginx.default.conf /etc/nginx/conf.d/default.conf
COPY 99-inject-env.sh /docker-entrypoint.d/99-inject-env.sh
RUN chmod +x /docker-entrypoint.d/99-inject-env.sh