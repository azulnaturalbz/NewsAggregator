# Use an official Python runtime as the base image
FROM python:3.8-slim
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install required packages
RUN pip install --no-cache-dir -r requirements.txt

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Define environment variable for Flask to run in production mode
ENV FLASK_APP=main.py
ENV FLASK_RUN_HOST=0.0.0.0

# Run gunicorn instead of the development server when the container launches
CMD ["gunicorn", "app:app", "-b", "0.0.0.0:5000"]
