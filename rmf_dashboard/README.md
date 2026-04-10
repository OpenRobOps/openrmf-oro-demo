# RMF Dashboard for OpenRMF ORO Demo

This directory contains a containerized build of the Open-RMF dashboard using the `rmf-dashboard-framework`. It provides a web UI to visualize maps, robots, doors, lifts and tasks, and is preconfigured to connect to the RMF API and trajectory servers used in the OpenRMF ORO demo.

The dashboard is designed to run fully inside Docker and be served by NGINX.

## 1. What is in this folder?

- `Dockerfile` – multi-stage build that:
	- Fetches the RMF web repositories listed in `rmf.repos`.
	- Installs dependencies via `pnpm`.
	- Builds the example dashboard under `packages/rmf-dashboard-framework/examples/target`.
	- Copies the built static site into an NGINX image.
- `dashboard/` – React/TypeScript entry point for this demo dashboard (see `dashboard/main.tsx` and `dashboard/index.html`).
- `dashboard_resources/` – Static resources such as logos and images used by the dashboard.
- `vite.config.ts` – Vite configuration used when building the example dashboard.
- `nginx.default.conf` – NGINX server configuration for serving the built dashboard.
- `99-inject-env.sh` – startup script that injects runtime environment variables into `index.html` so the dashboard points to the correct RMF services.

## 2. Building the dashboard image

Normally you do not build this image manually: it is built and run as the `dashboard` service from the top-level `docker-compose.yaml` in this repository.

To build it yourself from the repo root:

```bash
cd rmf_dashboard
docker build -t openrmf-rmf-dashboard .
```

This will:

1. Use `vcs import` and `rmf.repos` to fetch the necessary RMF web packages.
2. Install dependencies with `pnpm`.
3. Run the dashboard example build.
4. Produce an NGINX-based image that serves the built dashboard.

## 3. Runtime configuration (environment variables)

At runtime, the container expects two environment variables so it knows how to reach your RMF backend services:

- `RMF_SERVER_URL` – HTTP URL for the RMF API server (for example `http://localhost:8000`).
- `TRAJECTORY_SERVER_URL` – WebSocket URL for the trajectory server (for example `ws://localhost:8006`).

In the top-level `docker-compose.yaml`, the `dashboard` service is already configured with sensible defaults:

```yaml
environment:
	- RMF_SERVER_URL=http://localhost:8000
	- TRAJECTORY_SERVER_URL=ws://localhost:8006
```

You can override these when running `docker compose` if your API or trajectory server is exposed on different addresses.

### 3.1 How environment injection works

The HTML entry file `dashboard/index.html` defines placeholders:

```html
<script>
	window.RMF_SERVER_URL = "__RMF_SERVER_URL__";
	window.TRAJECTORY_SERVER_URL = "__TRAJECTORY_SERVER_URL__";
  
</script>
```

When the NGINX container starts, `/docker-entrypoint.d/99-inject-env.sh` runs and performs a simple replacement on `/usr/share/nginx/html/index.html`:

```bash
sed -i "s,__RMF_SERVER_URL__,${RMF_SERVER_URL},g" ${INDEX_HTML}
sed -i "s,__TRAJECTORY_SERVER_URL__,${TRAJECTORY_SERVER_URL},g" ${INDEX_HTML}
```

This means the dashboard always picks up the values provided as container environment variables, without needing to rebuild the image.

On the client side, `dashboard/main.tsx` reads these globals and passes them to the `RmfDashboard` component:

```tsx
<RmfDashboard
	apiServerUrl={window.RMF_SERVER_URL}
	trajectoryServerUrl={window.TRAJECTORY_SERVER_URL}
	...
/>
```

## 4. Using the dashboard in the OpenRMF ORO demo

In the context of the full demo:

- The RMF API server runs in the `api_server` service.
- The RMF trajectory server shares the same container and is exposed on a WebSocket port.
- This dashboard image is run by the `dashboard` service in the root `docker-compose.yaml` and published on `http://localhost:3011` by default.

Once the full stack is up (MQTT, ingest, web app, RMF core, and the simulated robots), navigate to the dashboard URL and you should see:

- A map view showing the OpenRMF layout.
- Robot states for the connected fleets.
- Task creation and task state views.
- A "Custom" tab that lets you design your own layout using the `rmf-dashboard-framework` micro-apps.

If you change where the RMF servers are running, simply adjust `RMF_SERVER_URL` and `TRAJECTORY_SERVER_URL` for the dashboard container and restart it; no rebuild is needed.

# Note
The `RMF_SERVER_URL` and `TRAJECTORY_SERVER_URL` environment variables only works on localhost setups where the dashboard container can reach the API and trajectory servers at `localhost`. If you are running the dashboard in a different environment (for example, if you deploy it to a cloud server or a different machine), you will need to set these environment variables to the appropriate addresses where the dashboard can reach the RMF services check RMF guides for this.