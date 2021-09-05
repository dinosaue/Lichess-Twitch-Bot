FROM python:slim

WORKDIR /app
ADD requirements.txt .
RUN pip install -r requirements.txt
ADD . .

ENTRYPOINT [ "python", "main.py" ]
