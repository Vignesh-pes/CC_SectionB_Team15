FROM python:3.9-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Make sure we have the python-dotenv package
RUN pip install python-dotenv

# Command to run the application
CMD ["python", "run.py"]