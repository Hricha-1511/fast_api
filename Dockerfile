FROM python:3.9

# Set environment variables
ENV NIXPACKS_PATH /opt/venv/bin:$NIXPACKS_PATH

# Set working directory
WORKDIR /app

# Copy source code
COPY . /app/

# Update pip
RUN pip install --upgrade pip==24.0

# Install dependencies within the virtual environment
RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install -r requirements.txt

# Command to run the application
CMD [ "python", "app.py" ]
