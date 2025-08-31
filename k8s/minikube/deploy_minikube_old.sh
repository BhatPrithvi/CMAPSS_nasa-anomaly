#!/bin/bash
set -e

NAMESPACE=nasa-anomaly
OUTPUT_DIR=$(pwd)/output

echo "[INFO] Starting Minikube with Docker driver + hostPath mount..."
minikube start --driver=docker --mount --mount-string="${OUTPUT_DIR}:/mnt/data/ml-output"

echo "[INFO] Setting Docker env to point builds into Minikube's Docker..."
eval $(minikube docker-env)

echo "[INFO] Building Docker image..."
docker build -t nasa-anomaly:latest .

echo "[INFO] Creating namespace (if not exists)..."
kubectl create namespace $NAMESPACE --dry-run=client -o yaml | kubectl apply -f -

echo "[INFO] Applying manifests..."
kubectl apply -n $NAMESPACE -f k8s/manifests/

echo "[INFO] Restarting pods to pick up new image..."
kubectl delete pods -n $NAMESPACE --all

echo "[INFO] Waiting for pods..."
kubectl get pods -n $NAMESPACE -w
