# Use a Python image with uv pre-installed
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

# install system dependencies
RUN apt-get update && apt-get install -y nodejs

# Expose ports
EXPOSE 8501

# Create a non-root user to work with
RUN useradd -ms /bin/bash appuser

# create the mount point and set devuser as owner
RUN mkdir -p /var/investorlab && chown appuser:appuser /var/investorlab

# Switch to the created user
USER appuser
WORKDIR /home/appuser

# Install the application code
ADD --exclude=**/.settings --exclude=**/.streamlit --chown=appuser:appuser ../src .

# Create the Python virtual environment without dev tools
ADD --chown=appuser:appuser ../uv.lock ../pyproject.toml .
RUN uv sync --no-dev

# Copy production configurations and scripts
COPY --chown=appuser:appuser docker/files .

# Start the application
CMD /bin/bash -c /home/appuser/run_app.sh
