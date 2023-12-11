FROM python:3.9-slim-bullseye

WORKDIR /workspace

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD [ "python3", "run.py" ]
