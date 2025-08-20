# Use a Python image with uv pre-installed
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

# install system dependencies
RUN apt-get update && apt-get install -y curl sqlite3

# install VS Code (code-server)
RUN apt-get update && apt-get install -y curl nodejs sqlite3
RUN curl -fsSL https://code-server.dev/install.sh | sh
# To have systemd start code-server now and restart on boot:
# sudo systemctl enable --now code-server@$USER

# Expose ports
EXPOSE 8080

# Create a non-root user to work with
RUN useradd -ms /bin/bash devuser

# create the mount point and set devuser as owner
RUN mkdir -p /var/investorlab && chown devuser:devuser /var/investorlab

# Switch to the created user
USER devuser
WORKDIR /home/devuser

# Install the application code
ADD --exclude=__pycache__  --chown=devuser:devuser ../Portfolio-Dashboard .

# Create the Python virtual environment
ADD --chown=devuser:devuser ../uv.lock ../pyproject.toml ../run_app.sh ./
RUN uv venv .venv
RUN uv export > requirements.txt
RUN uv pip install --requirements requirements.txt

# Override configuration files
COPY docker/config.toml .streamlit/config.toml
COPY docker/config.py .

# Copy the startup command
COPY docker/run_app.sh .

# Start the application
CMD ./run_app.sh
# Use this if the application won't start:
#CMD /bin/bash
