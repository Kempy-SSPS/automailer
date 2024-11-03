FROM python:3.12.5-alpine3.19
RUN apk add --no-cache tzdata
ENV TZ=Europe/Prague
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "main:app"]