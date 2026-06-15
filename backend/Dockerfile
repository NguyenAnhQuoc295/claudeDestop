FROM node:22-alpine AS dashboard-build

WORKDIR /build/dashboard-ui

COPY dashboard-ui/package*.json ./
RUN npm ci

COPY dashboard-ui/ ./
RUN npm run build


FROM python:3.11-slim

WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .
COPY --from=dashboard-build /build/dashboard-ui/dist /app/dashboard-ui/dist

ENV DASHBOARD_DIST_DIR=/app/dashboard-ui/dist

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
