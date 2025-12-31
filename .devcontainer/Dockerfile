FROM mcr.microsoft.com/devcontainers/python:3.14-bookworm

USER vscode
WORKDIR /workspace

RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/home/vscode/.local/bin:${PATH}"

CMD ["sleep", "infinity"]
