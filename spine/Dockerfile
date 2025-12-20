FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (for lxml probably)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libxml2-dev \
    libxslt-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code. 
# Note: we copy the whole spine directory structure to match imports like "from spine.src..."
# Assuming build context is the root 'Axiom_LCE' or we adjust. 
# BUT usually dockerfile is in spine/. So context is spine/.
# If context is spine/, then "from spine.src" might break if 'spine' package isn't root.
# Let's assume we run docker build from project root, or we fix the path.

# Let's adjust imports in python code? No, simpler to adjust python path.
# Or better: Copy content to /app/spine and set PYTHONPATH.

COPY . /app/spine
ENV PYTHONPATH=/app

# Expose port
EXPOSE 8000

# Command
CMD ["uvicorn", "spine.src.main:app", "--host", "0.0.0.0", "--port", "8000"]
