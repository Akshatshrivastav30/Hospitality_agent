# 1. Use an official Python runtime as a parent image
FROM python:3.12-slim

# 2. Set environment variables to ensure Python output is logged 
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 3. Set the working directory in the container
WORKDIR /app

# 4. Install system dependencies (needed for some Python packages)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 5. Copy the requirements file and install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copy the rest of your application code
COPY . /app/

# 7. Expose the port Django runs on
EXPOSE 8000

# 8. Command to run the application
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
