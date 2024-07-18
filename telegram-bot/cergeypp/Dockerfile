
ARG PYTHON_VERSION=3.12.3
FROM python:${PYTHON_VERSION}-slim as base

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN python -m pip install -r requirements.txt

COPY . .

CMD ["python", "-u","./main.py"]
