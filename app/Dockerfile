# Stage 1: Build and Test
FROM python:3.12.7 AS build

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code and test files
COPY . .

# Run tests
RUN PYTHONPATH=../app python -m unittest discover -v -s test

# Stage 2: Production
FROM python:3.12.7

# Set the working directory in the container
WORKDIR /app

# Copy only the necessary files from the build stage
COPY --from=build /app/model ./model
COPY --from=build /app/repository ./repository
COPY --from=build /app/service ./service
COPY --from=build /app/requirements.txt .
COPY --from=build /app/server.py .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt
RUN ls

# Expose the port the app runs on
EXPOSE 8080

# Command to run the application
CMD ["python", "server.py"]