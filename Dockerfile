FROM ubuntu:22.04

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Update package list and install essential tools
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    git \
    vim \
    nano \
    htop \
    tree \
    unzip \
    build-essential \
    python3 \
    python3-pip \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Create a non-root user for security
RUN useradd -m -s /bin/bash sandbox && \
    usermod -aG sudo sandbox && \
    echo "sandbox ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# Set working directory
WORKDIR /home/sandbox

# Copy configuration files
COPY sandbox.yml /home/sandbox/
COPY tools.json /home/sandbox/
COPY init.sh /home/sandbox/
COPY startup.py /home/sandbox/
COPY requirements.txt /home/sandbox/

# Install Python packages from requirements.txt
RUN pip3 install --no-cache-dir -r /home/sandbox/requirements.txt

# Create directories for projects and tools
RUN mkdir -p /home/sandbox/projects && \
    mkdir -p /home/sandbox/tools && \
    chmod +x /home/sandbox/init.sh && \
    chown -R sandbox:sandbox /home/sandbox

# Switch to non-root user
USER sandbox

# Set working directory to sandbox home
WORKDIR /home/sandbox

# Run initialization script
RUN /home/sandbox/init.sh

# Expose common ports
EXPOSE 8000 8888 3000

# Start the application server
CMD ["python3", "startup.py"]
