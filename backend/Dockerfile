
# Use the official Python runtime as base image.
FROM python:3.9-slim

# Set the working directory in the container to /app.
WORKDIR /app

# Copy the requirements file into the container at /app.
COPY requirements.txt .

# Install any dependencies.
RUN pip install --no-cache-dir -r requirements.txt

# Copy the app code to the container at /app.
COPY . .

# Expose the app on port 8000 (Render will override this).
EXPOSE 8000

# Run the app.
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]