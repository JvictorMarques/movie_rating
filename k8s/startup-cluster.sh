#!/usr/bin/env bash

CLUSTER_NAME="kind"
TAG_VERSION="latest"
IMAGE_TAG_PREFIX="movie-rating"
HOST_DOMAIN="movie-rating.local.com"

# Create a Kubernetes cluster using kind
if kind get clusters | grep -q "${CLUSTER_NAME}"; then
    echo "Cluster ${CLUSTER_NAME} already exists. Skipping cluster creation."
else
    kind create cluster --name "${CLUSTER_NAME}" --config kind-config.yaml
fi

docker build -t ${IMAGE_TAG_PREFIX}:${TAG_VERSION} ../app --target runtime
docker build -t ${IMAGE_TAG_PREFIX}-migrations:${TAG_VERSION} ../app --target migrations

# Load the Docker images into the kind cluster
kind load docker-image ${IMAGE_TAG_PREFIX}:${TAG_VERSION} --name "${CLUSTER_NAME}"
kind load docker-image ${IMAGE_TAG_PREFIX}-migrations:${TAG_VERSION} --name "${CLUSTER_NAME}"

# Apply the Kubernetes manifests to deploy the application
if ! helmfile apply -e local \
    --set app.image.tag="${TAG_VERSION}" \
    --set migrations.image.tag="${TAG_VERSION}" \
    --set app.ingress.host="${HOST_DOMAIN}"; then
    echo "Failed to apply Kubernetes manifests. Exiting."
    exit 1
fi

if ! grep -q "${HOST_DOMAIN}" /etc/hosts; then
    echo "Adding ${HOST_DOMAIN} to /etc/hosts"
    echo "127.0.0.1  ${HOST_DOMAIN}" | sudo tee -a /etc/hosts
fi

echo -e "Waiting for the application to be healthy\n"
until curl -s -o /dev/null http://${HOST_DOMAIN}/health; do
    echo "..."
    sleep 5
done

echo "Application is healthy and ready to use at http://${HOST_DOMAIN}"
