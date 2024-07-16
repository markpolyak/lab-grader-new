
ARG PYTHON_VERSION=3.12.3
FROM python:${PYTHON_VERSION}-slim as base

WORKDIR /usr/src/app

COPY requirements.txt ./

# Download dependencies as a separate step to take advantage of Docker's caching.
# Leverage a cache mount to /root/.cache/pip to speed up subsequent builds.
# Leverage a bind mount to requirements.txt to avoid having to copy them into
# into this layer.
RUN python -m pip install -r requirements.txt

# Copy the source code into the container.
COPY . .

# Run the application.
CMD ["python", "./main.py"]
