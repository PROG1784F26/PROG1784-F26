FROM mcr.microsoft.com/devcontainers/python:1-3.13-bookworm

ENV VIRTUAL_ENV=/home/vscode/.venv
ENV PATH="/home/vscode/.venv/bin:${PATH}"
COPY requirements-dev.txt /tmp/course-requirements.txt
RUN python -m venv /home/vscode/.venv \
    && /home/vscode/.venv/bin/python -m pip install --no-cache-dir -r /tmp/course-requirements.txt \
    && chown -R vscode:vscode /home/vscode/.venv \
    && echo '. /home/vscode/.venv/bin/activate' >> /home/vscode/.bashrc
