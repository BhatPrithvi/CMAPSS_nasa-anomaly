#!/bin/bash
set -e

NAMESPACE=nasa-anomaly

echo "[INFO] Deleting namespace $NAMESPACE..."
kubectl delete namespace $NAMESPACE --ignore-not-found

echo "[INFO] Deleting Minikube cluster..."
minikube delete
