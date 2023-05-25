FROM python:3.10.11
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY *.py .

ENV DB_HOST=db

EXPOSE 5000

CMD ["python", "server.py"]