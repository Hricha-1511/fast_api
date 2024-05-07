FROM python:3.9

# Set environment variables
ENV NIXPACKS_PATH /opt/venv/bin:$NIXPACKS_PATH

# Set working directory
WORKDIR /app

# Copy source code
COPY . /app/.

# Update pip
RUN pip install --upgrade pip==24.0

# Install dependencies
RUN python -m venv --copies /opt/venv && \
    . /opt/venv/bin/activate && \
    pip install -r requirements.txt

# Additional steps if any

# Command to run the application
CMD [ "python", "app.py" ]
