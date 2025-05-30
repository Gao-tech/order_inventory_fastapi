FROM public.ecr.aws/lambda/python:3.12

# Install system dependencies (Amazon Linux 2023 uses dnf)
RUN dnf install -y postgresql15-devel gcc python3-devel && dnf clean all

# Install Python dependencies first for layer caching
RUN pip install \
    "fastapi==0.109.0" \
    "pydantic==1.10.15" \
    "sqlmodel==0.0.24" \
    "mangum==0.19.0" \
    "psycopg2-binary==2.9.9"


# Copy application code
COPY src/ ${LAMBDA_TASK_ROOT}

# Set handler (verify path matches your code)
CMD ["app.main.handler"]