FROM python:3.12-slim
WORKDIR /opt/legacy
COPY . .
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 HOST=0.0.0.0 PORT=8080 LEGACY_DB=/var/lib/legacy/legacy.sqlite3
RUN mkdir -p /var/lib/legacy && python -m compileall -q app
EXPOSE 8080
CMD ["sh","-c","if [ ! -f /var/lib/legacy/legacy.sqlite3 ]; then cp /opt/legacy/data/legacy.sqlite3 /var/lib/legacy/legacy.sqlite3; fi; exec python -m app.server"]
