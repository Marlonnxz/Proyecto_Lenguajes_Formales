FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY Token.py .
COPY AnalisisLexico.py .
COPY SintacticoDinamico.py .
COPY reglas_acciones.py .
COPY reglas.json .
COPY compilador.py .
COPY main.py .
COPY servidor.py .
COPY consola.html .

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/info').read()"

# --proxy-headers: la app corre detras de Traefik + Cloudflare Tunnel
CMD ["uvicorn", "servidor:app", "--host", "0.0.0.0", "--port", "8000", "--proxy-headers", "--forwarded-allow-ips", "*"]
