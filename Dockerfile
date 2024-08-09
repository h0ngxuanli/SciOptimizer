FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y curl

# Install Ollama
RUN curl https://ollama.ai/install.sh | sh

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Expose both Ollama and Streamlit ports
EXPOSE 11434 8501

# Create a startup script
RUN echo '#!/bin/bash\n\
ollama serve &\n\
sleep 5\n\
ollama run llama3 &\n\
exec streamlit run interface/st_interface.py --server.port=8501 --server.address=0.0.0.0\n'\
> /app/start.sh && chmod +x /app/start.sh

# Use the startup script as the entrypoint
CMD ["/app/start.sh"]