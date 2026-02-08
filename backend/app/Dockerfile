FROM python:3.11.14-slim

WORKDIR /agent

COPY run.sh .
COPY agent.py .
COPY requirements.txt .
COPY .env .

CMD ["bash", "/agent/run.sh"]