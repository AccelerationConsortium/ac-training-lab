# Use Prefect v3 as the base image
FROM prefecthq/prefect:3-latest

# Set working directory
WORKDIR /app

# Install required Python packages
RUN pip install --no-cache-dir gradio_client

# Copy the flow script
COPY stirring.py .

# Set Prefect API URL (modify as needed)
ENV PREFECT_API_URL="http://192.168.2.144:4200/api"

# Default command (this is overridden by Prefect when executing a flow)
CMD ["python", "stirring.py"]
