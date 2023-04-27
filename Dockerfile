FROM python:3.9-slim

WORKDIR /app

# Copy the requirements file and install the dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application files
COPY . .

# Expose the port that the application will run on
EXPOSE 8000

# Set the environment variable for the database file
ENV DATABASE_URL sqlite:///./books.db

# Run the application
CMD [ "docker", "compose", "up" ]