#!/bin/bash
set -e

# -------------------------------
# CONFIGURATION
# -------------------------------
CLUSTER_NAME="nasa-anomaly"
NAMESPACE="nasa-anomaly"

# -------------------------------
# DELETE NAMESPACE
# -------------------------------
echo "[INFO] Deleting namespace $NAMESPACE if it exists..."
kubectl delete namespace $NAMESPACE --ignore-not-found
echo "[INFO] Namespace deletion requested. Pods may take a few seconds to terminate."

# -------------------------------
# DELETE KIND CLUSTER
# -------------------------------
echo "[INFO] Deleting Kind cluster: $CLUSTER_NAME..."
kind delete cluster --name $CLUSTER_NAME || echo "[INFO] Cluster $CLUSTER_NAME not found or already deleted."


echo "[INFO] Kind cluster stopped!"
