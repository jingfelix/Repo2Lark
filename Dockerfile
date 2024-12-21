FROM python:3.10-slim-bullseye

LABEL maintainer="jingfelix@outlook.com"

EXPOSE 3030

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1

# Install pip requirements
COPY requirements.txt .
RUN python -m pip install --no-cache-dir --upgrade repo2lark

CMD ["uvicorn", "repo2lark:app", "--port", "3030", "--host", "0.0.0.0", "--workers", "1"]
