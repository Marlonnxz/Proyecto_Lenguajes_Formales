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

CMD ["uvicorn", "servidor:app", "--host", "0.0.0.0", "--port", "8000"]
