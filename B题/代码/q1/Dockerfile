FROM python:3.10-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential cmake ninja-build libboost-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace
COPY . /workspace
RUN python -m pip install --no-cache-dir -r "B题/代码/q1/requirements-q1.txt"

WORKDIR /workspace/B题/代码
CMD ["python", "-m", "q1.run_q1"]
