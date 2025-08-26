# Use official python image as base
# An official python image built on a scaled Debian base with necessary packages only to keep the image small
FROM python:3.11-slim

# Set working directory inside the container
# Default directory inside the container. All commands will run in this directory
WORKDIR /app

# Copy requirements.txt first( for faster caching)
# This will install only the necessary packages
# If copied and run before coyping other files will cache layers, such that on code change if there are no change to requirements.txt dependencies will not be installed again
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files
# Copies everything from current folder on host machine into /app
COPY . .

# Create output folder inside container to save logs and results
RUN mkdir -p output
RUN mkdir -p output/plots

# Exposes port 8000 for Prometheus metrics
EXPOSE 8000

# Default command to run ML script in JSON format. This runs the ML script
CMD ["python","-u", "CMAPSS_IsolationForest.py"]


