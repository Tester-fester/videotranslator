# Use the official Python image from the Docker Hub
FROM python:3.12

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements.txt and install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy the Streamlit app and any other files to the container
COPY . .

# Expose the port for the app to run (Streamlit uses port 8501 by default)
EXPOSE 8501

# Define the command to run the app
CMD ["streamlit", "run", "your_app.py"]
