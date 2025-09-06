#!/bin/bash
set -e

# --- Configuration ---
NAMESPACE="nasa-anomaly"
OUTPUT_DIR=$(pwd)/output
IMAGE_NAME="nasa-anomaly:latest"
APP_LABEL="cmapss-isolationforest"
CONTAINER_PORT=8000
HOST_PORT=8000

# --- Step 0: Ensure output folder exists ---
mkdir -p $OUTPUT_DIR

# --- Step 1: Start Minikube ---
echo "[INFO] Starting Minikube with Docker driver + hostPath mount..."
minikube start --driver=docker --mount --mount-string="${OUTPUT_DIR}:/mnt/data/ml-output"

# --- Step 2: Point Docker builds to Minikube ---
echo "[INFO] Setting Docker env to point builds into Minikube's Docker..."
eval $(minikube docker-env)

# --- Step 3: Build Docker image ---
echo "[INFO] Building Docker image..."
docker build -t $IMAGE_NAME .

# --- Step 4: Create namespace if not exists ---
echo "[INFO] Creating namespace (if not exists)..."
kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -

# --- Step 5: Apply manifests ---
echo "[INFO] Applying manifests..."
kubectl apply -n $NAMESPACE -f k8s/manifests/

# --- Step 6: Restart pods to pick up new image ---
echo "[INFO] Restarting pods..."
kubectl delete pods -n $NAMESPACE --all

# --- Step 7: Wait for pods ---
echo "[INFO] Waiting for pods to be ready..."
kubectl wait --for=condition=Ready pods --all -n $NAMESPACE --timeout=180s
kubectl get pods -n $NAMESPACE -w &

# --- Step 8: Get first pod name dynamically ---
POD=$(kubectl get pod -n $NAMESPACE -l app=$APP_LABEL -o jsonpath='{.items[0].metadata.name}')

# --- Step 9: Optional: copy output to host automatically (after pod finishes) ---
# echo "[INFO] Copying output from pod to host..."
kubectl cp -n $NAMESPACE $POD:/app/output $OUTPUT_DIR

# --- Step 10: Port forward so Flask app is accessible ---
echo "[INFO] Forwarding port $CONTAINER_PORT -> $HOST_PORT ..."
kubectl port-forward -n $NAMESPACE $POD $HOST_PORT:$CONTAINER_PORT &

# --- Step 11: Show user where to access ---
echo "[INFO] You can now view the app in your browser at:"
echo "http://127.0.0.1:$HOST_PORT"
echo "Output folder on host: $OUTPUT_DIR"
