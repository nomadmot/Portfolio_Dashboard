# Use a Python image with uv pre-installed
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

# install system dependencies
RUN apt-get update && apt-get install -y nodejs sqlite3

# Expose ports
EXPOSE 8080

# Create a non-root user to work with
RUN useradd -ms /bin/bash appuser

# create the mount point and set devuser as owner
RUN mkdir -p /var/investorlab && chown appuser:appuser /var/investorlab

# Switch to the created user
USER appuser
WORKDIR /home/appuser

# Install the application code
ADD --exclude=**/.settings --exclude=**/.streamlit --chown=appuser:appuser ../src .

# Create the Python virtual environment
ADD --chown=appuser:appuser ../uv.lock ../pyproject.toml ../run_app.sh ./
RUN uv venv .venv
RUN uv export > requirements.txt
RUN uv pip install --requirements requirements.txt

# Copy production configurations and scripts
COPY --chown=appuser:appuser docker/files .

# Start the application
CMD ./run_app.sh
# Use this if the application won't start:
#CMD /bin/sh
