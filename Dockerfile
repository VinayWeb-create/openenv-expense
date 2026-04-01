# Base Image
FROM python:3.9-slim

# Set Working Directory
WORKDIR /app

# Copy Requirements and Install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy Project Files
COPY . .

# Expose FastAPI Port
EXPOSE 8000

# Run the FastAPI App
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
