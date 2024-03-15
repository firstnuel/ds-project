# Use an official lightweight Python image
FROM python:3.8-slim

# Set the working directory in the container to /app
WORKDIR /app

# Install system dependencies (if any)
# RUN apt-get update && apt-get install -y <your-dependencies> && rm -rf /var/lib/apt/lists/*

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 5002 available to the world outside this container
EXPOSE 5003

# Environment variable for OpenAI API Key
# Note: It's recommended to set this at runtime for security reasons
# ENV OPENAI_API_KEY your_openai_api_key_here

# Command to run the Flask application
CMD ["python", "analysis.py"]
