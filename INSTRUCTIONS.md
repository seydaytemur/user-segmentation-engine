# How to Run

This project is fully containerized using Docker to ensure a consistent and isolated environment.

## 1. Prerequisites
Ensure that Docker Desktop is installed and running on your system.

## 2. Building the Image
Open your terminal in the project's root directory and execute the following command to build the Docker image:

```bash
docker build -t peak-internship-solution .
```

## 3. Running the Container
Once the image is built, you can start the application by specifying the PORT environment variable (e.g., 3000):

```bash
docker run -e PORT=3000 -p 3000:3000 peak-internship-solution
```

## 4. Verification & Testing

### Integrated Test Suite
Open your browser and navigate to [http://localhost:3000/evaluate](http://localhost:3000/evaluate) to access the interactive test interface.

### Automated Test Script
Alternatively, while the server is running, you can execute the automated test script from the root directory:

```bash
python verify_server.py
```