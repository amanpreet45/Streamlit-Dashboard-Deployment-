 Streamlit Dashboard Deployment via Docker + Ngrok
1. Objective
This document explains how to run a Streamlit Learning Dashboard application locally using:
Python + Streamlit app


Docker container (portable environment)


Ngrok tunnel (public URL access)


This setup is useful when:
  you want to share your local Streamlit dashboard with anyone
  you want stable deployment-like environment without cloud hosting
 you want to run "production-style" access

2. Architecture Overview
Flow
Streamlit app runs inside Docker container


Docker exposes Streamlit port 8501


Ngrok tunnels local port → provides public HTTPS URL


 Diagram (Simple)
[User Browser] ---> https://xxxxx.ngrok-free.app
                      |
                      v
                 [Ngrok Tunnel]
                      |
                      v
          localhost:8501 (Docker Port)
                      |
                      v
           [Streamlit App inside Docker]


3. Prerequisites
Make sure you have installed:
 System Requirements
macOS / Linux / Windows


Minimum RAM: 4GB


Disk: 1GB free


 Installations
Docker Desktop


Check:


docker --version

Ngrok


Check:


ngrok version

Python (optional if using only Docker)





4. Project Folder Structure
Recommended structure:
devops-learning-dashboard/
│
├── app.py
├── resources.yaml
├── requirements.txt
├── README.md
└── Dockerfile


5. Streamlit App Configuration
In your app.py, best practice is to run Streamlit with:
st.set_page_config(
    page_title="DevOps Learning Dashboard",
    layout="wide"
)


6. Dockerfile (Recommended)
Create Dockerfile in your project root:
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.headless=true"]


7. Build Docker Image
Run from project folder:
docker build -t devops-dashboard .

Check images:
docker images


8. Run Streamlit Dashboard in Docker
Run container:
docker run -p 8501:8501 devops-dashboard

Now open in browser:
 Local URL
http://localhost:8501


9. Verify Docker Container is Running
In another terminal:
docker ps

You should see your container running and port mapped:
0.0.0.0:8501->8501/tcp


10. Expose Public Link Using Ngrok
Ngrok command:
ngrok http 8501

Output will show public links:
 Example:
Forwarding https://abcd-1234.ngrok-free.app -> http://localhost:8501

Now anyone can access your dashboard using the ngrok HTTPS URL.

11. Common Problems & Fixes
1) Streamlit not loading inside ngrok
Make sure Streamlit uses 0.0.0.0
If you see:
 ❌ site not reachable
Fix:
 Docker command must map correctly:
docker run -p 8501:8501 devops-dashboard

and Streamlit must run with:
--server.address=0.0.0.0


2) Ngrok shows blank/timeout
Possible causes:
container stopped


heavy dashboard load


too many PDFs or scanning huge folder


Fix:
ensure container is running


reduce file scanning load


cache resources.yaml load



✅ 3) Slow dashboard performance
Major reasons:
you scan thousands of PDFs every refresh


not using caching (@st.cache_data)


large YAML parsed every time


Solution:
 ✅ cache reading YAML
 ✅ cache scanning books folder
 ✅ load only when tab is selected

12. Recommended Best Practices
 Enable caching:
@st.cache_data
def load_resources():
    ...

 Avoid loading entire PDFs list at startup
 Load only when Books tab is opened.






13. Commands Summary
Task
Command
Build Docker image
docker build -t devops-dashboard .
Run container
docker run -p 8501:8501 devops-dashboard
Start ngrok
ngrok http 8501
View container
docker ps
Stop container
docker stop <container_id>




