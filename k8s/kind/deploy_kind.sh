#!/bin/bash
set -e

# -------------------------------
# CONFIGURATION
# -------------------------------
CLUSTER_NAME="nasa-anomaly"
NAMESPACE="nasa-anomaly"
OUTPUT_DIR="$(pwd)/output"
IMAGE_NAME="nasa-anomaly:latest"   # Local image, no Docker Hub
SERVICE_NAME="cmapss-isolationforest"
LOCAL_PORT=8000
CONTAINER_PORT=8000

# -------------------------------
# CREATE KIND CLUSTER
# -------------------------------
echo "[INFO] Creating Kind cluster: $CLUSTER_NAME..."
kind create cluster --name $CLUSTER_NAME || echo "[INFO] Cluster already exists. Skipping creation."

# -------------------------------
# BUILD LOCAL DOCKER IMAGE
# -------------------------------
echo "[INFO] Building Docker image locally..."
docker build -t $IMAGE_NAME .

# -------------------------------
# LOAD LOCAL IMAGE INTO KIND
# -------------------------------
echo "[INFO] Loading local Docker image into Kind cluster..."
kind load docker-image $IMAGE_NAME --name $CLUSTER_NAME

# -------------------------------
# CREATE NAMESPACE
# -------------------------------
echo "[INFO] Creating namespace: $NAMESPACE..."
kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -

# -------------------------------
# APPLY K8S MANIFESTS
# -------------------------------
echo "[INFO] Applying Kubernetes manifests..."
kubectl apply -n $NAMESPACE -f k8s/manifests/

# -------------------------------
# WAIT FOR PODS TO BE READY
# -------------------------------
echo "[INFO] Waiting for pods to be ready..."
kubectl wait --for=condition=Ready pods --all -n $NAMESPACE --timeout=180s
kubectl get pods -n $NAMESPACE

# -------------------------------
# PORT FORWARD TO LOCAL HOST
# -------------------------------
echo "[INFO] Port-forwarding $SERVICE_NAME to localhost:$LOCAL_PORT..."
echo "Use Ctrl+C to stop port-forwarding after testing."
kubectl port-forward svc/$SERVICE_NAME $LOCAL_PORT:$CONTAINER_PORT -n $NAMESPACE &

# -------------------------------
# OPTIONAL: COPY OUTPUT FROM POD TO HOST
# -------------------------------
read -p "Do you want to copy ML output from the pod to host? (y/n): " COPY_OUTPUT
if [[ "$COPY_OUTPUT" == "y" ]]; then
    POD_NAME=$(kubectl get pods -n $NAMESPACE -l app=$SERVICE_NAME -o jsonpath="{.items[0].metadata.name}")
    mkdir -p $OUTPUT_DIR
    echo "[INFO] Copying output from Pod $POD_NAME:/app/output to host $OUTPUT_DIR..."
    kubectl cp $NAMESPACE/$POD_NAME:/app/output $OUTPUT_DIR
    echo "[INFO] Output copied to $OUTPUT_DIR"
fi

echo "[INFO] Deployment complete!"
echo "Access Flask API at http://localhost:$LOCAL_PORT/"
