FROM public.ecr.aws/lambda/python:3.12

# Install system dependencies (Amazon Linux 2023 uses dnf)
RUN dnf install -y \
    gcc \
    postgresql15-devel \
    python3-devel \
    && dnf clean all

# Install Python dependencies first for layer caching
RUN pip install \
    psycopg2-binary==2.9.10 \
    fastapi==0.115.2 \
    sqlmodel==0.0.24 \
    mangum==0.19.0

# Copy application code
COPY src/ ${LAMBDA_TASK_ROOT}

# Set handler (verify path matches your code)
CMD ["app.main.handler"]