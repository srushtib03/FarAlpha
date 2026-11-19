# Flask + MongoDB on Kubernetes

A containerized Flask application deployed on Kubernetes using Minikube. The application supports REST APIs for inserting and retrieving data from MongoDB, persistent storage, internal service discovery, and automatic horizontal scaling based on CPU utilization.

---

## 1. Project Overview

This project deploys a Flask application and MongoDB on a local Kubernetes cluster.

### Features

- Flask REST API
- MongoDB database with authentication
- MongoDB StatefulSet
- Persistent storage using PersistentVolume (PV) and PersistentVolumeClaim (PVC)
- Flask Deployment with 2 initial replicas
- NodePort Service to expose Flask externally
- Internal ClusterIP Service for MongoDB
- Kubernetes Secret for database credentials and connection URI
- CPU and memory requests and limits
- Horizontal Pod Autoscaler (HPA)
- CPU target utilization: 70%
- Minimum replicas: 2
- Maximum replicas: 5

---

## 2. Architecture

\`\`\`
                        Client
                          |
                          |
                    NodePort :30080
                          |
                    Flask Service
                          |
             +------------+------------+
             |                         |
         Flask Pod 1               Flask Pod 2
             |                         |
             +------------+------------+
                          |
                  MongoDB Service
                 mongodb:27017
                          |
                    MongoDB Pod
                    mongodb-0
                          |
                     MongoDB PVC
                          |
                     MongoDB PV
\`\`\`

The Flask application is exposed externally using a NodePort Service. MongoDB is accessible internally through a ClusterIP Service and is not directly exposed externally.

The Flask Deployment is managed by a Horizontal Pod Autoscaler, which adjusts the number of replicas based on CPU utilization.

---

## 3. Technologies Used

- Python
- Flask
- MongoDB
- Docker
- Kubernetes
- Minikube
- kubectl
- Horizontal Pod Autoscaler (HPA)

---

## 4. Project Structure

\`\`\`
FarAlpha-Assignment/
│
├── app/
│   ├── app.py
│   └── requirements.txt
│
├── k8s/
│   ├── flask-deployment.yaml
│   ├── flask-service.yaml
│   ├── flask-hpa.yaml
│   ├── mongodb-secret.yaml
│   ├── mongodb-pv.yaml
│   ├── mongodb-pvc.yaml
│   ├── mongodb-statefulset.yaml
│   └── mongodb-service.yaml
│
├── screenshots/
│   ├── hpa-scale-up.png
│   ├── hpa-scale-down.png
│   └── flask-2-replicas.png
│
├── Dockerfile
└── .dockerignore
\`\`\`

---

## 5. Flask API Endpoints

### GET /

Returns a welcome message along with the current UTC timestamp.

Example:

\`\`\`
Welcome to the Flask app! The current time is: <timestamp>
\`\`\`

### GET /health

Returns the health status of the Flask application.

Response:

\`\`\`json
{
  "status": "healthy"
}
\`\`\`

### GET /data

Retrieves documents stored in MongoDB.

Example response:

\`\`\`json
[
  {
    "name": "Srushti",
    "message": "MongoDB Kubernetes integration test",
    "environment": "minikube"
  }
]
\`\`\`

### POST /data

Inserts a JSON document into MongoDB.

Example request:

\`\`\`bash
curl -X POST http://localhost:5000/data \
  -H "Content-Type: application/json" \
  -d '{"name":"Example","message":"Hello MongoDB","environment":"minikube"}'
\`\`\`

Example response:

\`\`\`json
{
  "status": "Data inserted successfully",
  "inserted_id": "<MongoDB-generated-id>"
}
\`\`\`

---

## 6. Docker

### Dockerfile

The application is containerized using a Python 3.11 slim image and runs using Gunicorn.

The container exposes port 5000.

### Build the Docker image

\`\`\`bash
docker build -t flask-mongodb-app:v1 .
\`\`\`

### Verify the image

\`\`\`bash
docker images | grep flask-mongodb-app
\`\`\`

---

## 7. Kubernetes Deployment using Minikube

### Prerequisites

- Docker Desktop
- Minikube
- kubectl

### Start Minikube

\`\`\`bash
minikube start --driver=docker --cpus=3 --memory=3500
\`\`\`

### Enable Metrics Server

\`\`\`bash
minikube addons enable metrics-server
\`\`\`

Verify node status:

\`\`\`bash
kubectl get nodes
\`\`\`

---

## 8. Deploy MongoDB

MongoDB is deployed using a StatefulSet with persistent storage.

### Resources

- MongoDB StatefulSet
- MongoDB ClusterIP Service
- PersistentVolume
- PersistentVolumeClaim
- Kubernetes Secret for credentials

### Apply MongoDB resources

\`\`\`bash
kubectl apply -f k8s/mongodb-secret.yaml
kubectl apply -f k8s/mongodb-pv.yaml
kubectl apply -f k8s/mongodb-pvc.yaml
kubectl apply -f k8s/mongodb-statefulset.yaml
kubectl apply -f k8s/mongodb-service.yaml
\`\`\`

Verify:

\`\`\`bash
kubectl get pods
kubectl get pv
kubectl get pvc
kubectl get services
\`\`\`

The MongoDB pod should reach the Running state, and the PVC should be Bound.

---

## 9. Deploy Flask

The Flask Deployment starts with two replicas.

The application container retrieves the MongoDB connection URI from the Kubernetes Secret through an environment variable.

### Apply Flask resources

\`\`\`bash
kubectl apply -f k8s/flask-deployment.yaml
kubectl apply -f k8s/flask-service.yaml
\`\`\`

Verify:

\`\`\`bash
kubectl get deployments
kubectl get pods
kubectl get services
\`\`\`

---

## 10. MongoDB Connection and Kubernetes DNS

Flask connects to MongoDB using the Kubernetes Service DNS name:

\`\`\`
mongodb:27017
\`\`\`

The connection URI is provided through a Kubernetes Secret.

The hostname \`mongodb\` resolves to the ClusterIP of the MongoDB Service within the Kubernetes cluster.

Using the Service DNS name instead of a pod IP is important because pod IP addresses can change when pods are recreated. The Service provides a stable endpoint for internal communication.

---

## 11. Persistent Storage

MongoDB uses a PersistentVolume and PersistentVolumeClaim.

- PV provides storage capacity.
- PVC requests storage for MongoDB.
- MongoDB mounts the persistent volume at \`/data/db\`.

Persistent storage allows database files to survive MongoDB pod recreation, subject to the configured volume and reclaim policy.

---

## 12. Resource Requests and Limits

The Flask and MongoDB containers use the following resource configuration.

| Resource | Request | Limit |
|---|---:|---:|
| CPU | 200m | 500m |
| Memory | 250Mi | 500Mi |

### CPU

- 200m CPU request: Kubernetes uses this as the baseline CPU allocation for scheduling and CPU utilization calculations.
- 500m CPU limit: the container is limited to a maximum of 0.5 CPU core.

### Memory

- 250Mi memory request: memory reservation used for scheduling.
- 500Mi memory limit: maximum memory usage allowed for the container before it may be terminated due to memory pressure.

Requests help Kubernetes schedule workloads. Limits restrict the resources a container can consume.

---

## 13. Horizontal Pod Autoscaler (HPA)

The Flask Deployment is configured with an HPA using CPU utilization.

| Parameter | Value |
|---|---:|
| Minimum replicas | 2 |
| Maximum replicas | 5 |
| CPU target utilization | 70% |
| Metric | CPU |

### Apply HPA

\`\`\`bash
kubectl apply -f k8s/flask-hpa.yaml
\`\`\`

Verify:

\`\`\`bash
kubectl get hpa
kubectl describe hpa flask-hpa
\`\`\`

### CPU utilization calculation

HPA CPU utilization is calculated relative to the CPU requests configured for the containers.

With a CPU request of 200m:

\`\`\`
70% of 200m = 140m CPU
\`\`\`

The HPA uses CPU metrics from the Kubernetes Metrics Server to determine whether additional replicas are needed.

---

## 14. Autoscaling Test Results

The HPA was tested by generating CPU load inside a Flask pod.

### Scale-up test

During the CPU load test, CPU utilization exceeded the 70% target.

Observed scaling:

| CPU utilization observed | Flask replicas observed |
|---:|---:|
| 95% | 2 → 3 |
| 126% | 3 → 4 |

The HPA increased the number of Flask replicas from 2 to 4 in response to CPU load.
<img width="1438" height="292" alt="image" src="https://github.com/user-attachments/assets/91e0ba3c-4022-431a-b615-719d18476e6c" />
<img width="1370" height="214" alt="image" src="https://github.com/user-attachments/assets/133cf0be-b619-4582-bed1-06e1222ead72" />
![Uploading image.png…]()


### Scale-down test

After CPU load was stopped, CPU utilization returned to approximately 2–4%.

The HPA subsequently reduced the replica count from 4 back to 2.

### Observed scaling lifecycle

\`\`\`
Normal load:       2 replicas
CPU load:          2 → 3 → 4 replicas
Load stopped:      4 → 2 replicas
\`\`\`

This demonstrates automatic scale-up and scale-down behavior.

---

## 15. Testing the Application

### Check pods

\`\`\`bash
kubectl get pods
\`\`\`

### Check resource usage

\`\`\`bash
kubectl top pods
\`\`\`

### Check HPA

\`\`\`bash
kubectl get hpa flask-hpa
\`\`\`

### Access the Flask Service

On macOS with Minikube Docker driver, run:

\`\`\`bash
minikube service flask-service --url
\`\`\`

Keep the terminal running because Minikube may maintain a tunnel.

Use the URL returned by Minikube in another terminal.

### Test homepage

\`\`\`bash
curl http://127.0.0.1:<PORT>/
\`\`\`

### Test health endpoint

\`\`\`bash
curl http://127.0.0.1:<PORT>/health
\`\`\`

### Insert data

\`\`\`bash
curl -X POST http://127.0.0.1:<PORT>/data \
  -H "Content-Type: application/json" \
  -d '{"name":"Example","message":"Kubernetes test","environment":"minikube"}'
\`\`\`

### Retrieve data

\`\`\`bash
curl http://127.0.0.1:<PORT>/data
\`\`\`

Replace \`<PORT>\` with the port from the Minikube service URL.

---

## 16. Screenshots

Screenshots demonstrating deployment and autoscaling are stored in the \`screenshots/\` directory.

### HPA Scale-up

Shows CPU utilization exceeding the configured target and the Flask replicas increasing from 2 to 4.

### HPA Scale-down

Shows CPU utilization returning to normal and replicas decreasing back to 2.

### Flask replicas

Shows the Flask pods in their stable state.

---

## 17. Troubleshooting

### Pods show CreateContainerConfigError

Inspect the pod:

\`\`\`bash
kubectl describe pod <pod-name>
\`\`\`

Check for missing Kubernetes Secrets or missing Secret keys.

### Pods show ImagePullBackOff

Verify that the image exists inside Minikube:

\`\`\`bash
minikube image ls
\`\`\`

If the image was built in Docker Desktop, load it into Minikube:

\`\`\`bash
docker save -o /tmp/flask-mongodb-app-v1.tar flask-mongodb-app:v1
minikube image load /tmp/flask-mongodb-app-v1.tar
\`\`\`

### CPU metrics unavailable

Check:

\`\`\`bash
kubectl top pods
kubectl get hpa
\`\`\`

Ensure Metrics Server is enabled:

\`\`\`bash
minikube addons enable metrics-server
\`\`\`

### MongoDB connectivity issues

Check:

\`\`\`bash
kubectl get pods
kubectl get services
kubectl describe pod mongodb-0
\`\`\`

Ensure the MongoDB Service is named \`mongodb\` and the connection URI uses the correct Service hostname, port, credentials, and authentication database.

### NodePort access on macOS

Use:

\`\`\`bash
minikube service flask-service --url
\`\`\`

With the Docker driver on macOS, the tunnel terminal may need to remain open while accessing the application.

---

## 18. Security Notes

- MongoDB credentials are stored in a Kubernetes Secret.
- MongoDB is exposed internally using ClusterIP, not NodePort.
- The Flask application accesses MongoDB through the internal Service DNS name.
- Kubernetes Secrets are not automatically equivalent to encrypted secrets management. For production deployments, use stronger secret management and avoid committing credentials to GitHub.

---

## 19. Cleanup

To delete the application resources:

\`\`\`bash
kubectl delete -f k8s/flask-hpa.yaml
kubectl delete -f k8s/flask-service.yaml
kubectl delete -f k8s/flask-deployment.yaml
kubectl delete -f k8s/mongodb-service.yaml
kubectl delete -f k8s/mongodb-statefulset.yaml
kubectl delete -f k8s/mongodb-pvc.yaml
kubectl delete -f k8s/mongodb-pv.yaml
kubectl delete -f k8s/mongodb-secret.yaml
\`\`\`

To stop Minikube:

\`\`\`bash
minikube stop
\`\`\`

---

## 20. Conclusion

This project demonstrates containerization and deployment of a Flask application with MongoDB on Kubernetes. It includes internal service discovery, persistent storage, health checks, resource management, external service access, and CPU-based horizontal autoscaling.

The HPA was verified through an actual CPU load test, demonstrating scaling from 2 to 4 Flask replicas and returning to 2 replicas after the load was removed.

## Configure MongoDB Credentials

Before deploying, create your local credentials file from the example template:

    cp k8s/mongodb-secret.example.yaml k8s/mongodb-secret.yaml

Replace CHANGE_ME with your own MongoDB password in the generated file.

    nano k8s/mongodb-secret.yaml

The actual credentials file is excluded from Git to prevent accidentally exposing database credentials.

## Docker Hub: Build and Push the Image

Replace YOUR_DOCKERHUB_USERNAME with your Docker Hub username.

### Build the Docker image

    docker build -t flask-mongodb-app:v1 .

### Tag the image for Docker Hub

    docker tag flask-mongodb-app:v1 YOUR_DOCKERHUB_USERNAME/flask-mongodb-app:v1

### Login to Docker Hub

    docker login

### Push the image

    docker push YOUR_DOCKERHUB_USERNAME/flask-mongodb-app:v1

After publishing, update the image field in `k8s/flask-deployment.yaml` to:

    image: YOUR_DOCKERHUB_USERNAME/flask-mongodb-app:v1

When using a published image in Kubernetes, set:

    imagePullPolicy: Always

