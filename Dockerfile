FROM --platform=linux/amd64 python:3.10-slim

RUN apt-get update
COPY requirements.txt ./requirements.txt
RUN pip3 install --upgrade pip && pip3 install --no-cache-dir -r requirements.txt

COPY . ./

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
