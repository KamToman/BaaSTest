# Use an official Ubuntu base image
# Use an official Ubuntu base image
FROM ubuntu:20.04

# Set environment variable to not prompt during apt-get installations
ENV DEBIAN_FRONTEND=noninteractive

# Install necessary dependencies and tools
RUN apt-get update && apt-get install -y \
    unixodbc \
    unixodbc-dev \
    libpq-dev \
    odbcinst \
    curl \
    gnupg \
    lsb-release \
    ca-certificates \
    python3 \
    python3-pip \
    && curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/ubuntu/$(lsb_release -rs)/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql17

# Verify driver installation (optional, for debugging purposes)
RUN odbcinst -q -d

# Install Python dependencies (assuming you have a requirements.txt)
WORKDIR /app
COPY . /app
RUN pip3 install -r requirements.txt

# Expose the port that your app runs on
EXPOSE 80

# Command to run your FastAPI app (or the appropriate command for your project)
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "80"]

