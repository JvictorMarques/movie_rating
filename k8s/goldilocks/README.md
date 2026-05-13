# Goldilocks

[Goldilocks](https://goldilocks.docs.fairwinds.com/) is a Fairwinds tool that analyzes resource usage and recommends `requests` and `limits` for your containers, based on VPA (Vertical Pod Autoscaler) data.

## Prerequisites

- `helm` installed
- `kubectl` configured against your cluster

## Installation

Add the Fairwinds Helm repository and install Goldilocks using the `values.yaml` in this directory:

```bash
helm repo add fairwinds-stable https://charts.fairwinds.com/stable
helm repo update

helm install goldilocks fairwinds-stable/goldilocks \
  --namespace goldilocks \
  --create-namespace \
  -f values.yaml
```

> The `values.yaml` already enables VPA and metrics-server as sub-charts, so no separate installation is needed.

## Important: metrics-server TLS flag

When running on a local cluster (e.g. Kind), the metrics-server fails to scrape kubelet metrics due to self-signed certificates. To fix this, add the `--kubelet-insecure-tls` flag to the metrics-server args in `values.yaml`:

```yaml
metrics-server:
  enabled: true
  apiService:
    create: true
  args:
    - --kubelet-insecure-tls
```

Without this flag, the metrics-server will not collect resource data and Goldilocks will show no recommendations.

## Enabling namespace monitoring

Label the namespaces you want Goldilocks to analyze:

```bash
kubectl label namespace <your-namespace> goldilocks.fairwinds.com/enabled=true
```

## Accessing the dashboard

Forward the dashboard port locally:

```bash
kubectl port-forward svc/goldilocks-dashboard 8080:80 -n goldilocks
```

Then open `http://localhost:8080` in your browser.

## Reference

- [Goldilocks documentation](https://goldilocks.docs.fairwinds.com/installation/#installation-2)
- [Fairwinds Helm charts](https://github.com/FairwindsOps/charts/tree/master/stable/goldilocks)
