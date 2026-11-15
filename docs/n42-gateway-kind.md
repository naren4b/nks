# Local Kubernetes Gateway with kind and N42 Gateway

Published: 2026-11-15

Set up one local Gateway API entry point on a multi-node kind cluster. The
shared N42 Gateway controller stays stable while each application adds its own
Service and HTTPRoute.

## What You Will Build

The cluster uses the existing kind port mappings: host port 8080 reaches port
80 on the control-plane node. N42 Gateway listens there and routes requests to
a Kubernetes Service.

~~~~mermaid
flowchart LR
  D["Developer on localhost:8080"] --> K["kind control-plane port 80"]
  K --> N["N42 Gateway and Gateway API"]
  N --> S["Service and application Pods"]
~~~~

The NKS repository owns the generic cluster and controller setup. An
application repository owns its Deployment, Service, and HTTPRoute. A new
application route should not require changes to the shared controller
installation.

## Prerequisites

Use [Local Kubernetes with kind](mykindk8scluster.md).

| Component | Version or setting |
| --- | --- |
| Docker Engine | 29.1.3 from the current WSL2 lab |
| kind | v0.33.0 for new cluster creation |
| Kubernetes node image | v1.34.11, pinned by digest in the kind guide |
| kubectl | v1.35.3, one minor newer than the Kubernetes API server |
| Helm | Version 3 |
| N42 Gateway | Stable v0.16.3, Helm chart 0.16.3 |
| Gateway API | Standard channel v1.7.0 |

The lab previously used kind v0.20.0 and tried a Kubernetes v1.37.0 node
image. That combination failed during kubeadm initialization because the old
configuration used the removed kubeadm.k8s.io/v1beta3 API. Keep the kind
binary and Kubernetes node image aligned. This guide uses the known local
Kubernetes v1.34.11 image.

N42 Gateway v0.16.3 is the current stable line and provides **partial**
Gateway API support. This guide uses only a basic GatewayClass, Gateway, and
HTTPRoute. N42 Gateway v0.17 is still alpha. Check the
[N42 Gateway supported versions](https://github.com/n42-gateway/n42-gateway#use-n42-gateway)
and [Gateway API releases](https://github.com/kubernetes-sigs/gateway-api/releases)
before upgrading.

## Implementation

### 1. Confirm the cluster and host port

Set the intended context explicitly. The cluster config must map host port
8080 to control-plane container port 80, as in the kind guide.

~~~~sh
CLUSTER_NAME=dev-cluster
CONTEXT="kind-$CLUSTER_NAME"

kubectl --context "$CONTEXT" get nodes
kubectl --context "$CONTEXT" get storageclass
~~~~

### 2. Install the Gateway API CRDs

Install the Standard channel CRDs once per cluster:

~~~~sh
kubectl --context "$CONTEXT" apply --server-side \
  -f https://github.com/kubernetes-sigs/gateway-api/releases/download/v1.7.0/standard-install.yaml
~~~~

Confirm the core resources exist:

~~~~sh
kubectl --context "$CONTEXT" get crd gatewayclasses.gateway.networking.k8s.io
kubectl --context "$CONTEXT" get crd gateways.gateway.networking.k8s.io
kubectl --context "$CONTEXT" get crd httproutes.gateway.networking.k8s.io
~~~~

### 3. Install N42 Gateway

N42 Gateway v0.16 still uses the HAProxy Ingress name for its Helm chart and
configuration keys. This is the upstream stable installation path.

Save the following as n42-gateway-values.yaml:

~~~~yaml
controller:
  ingressClassResource:
    enabled: false
  kind: DaemonSet
  daemonset:
    useHostPort: true
  service:
    type: ClusterIP
  nodeSelector:
    node-role.kubernetes.io/control-plane: ""
  tolerations:
    - key: node-role.kubernetes.io/control-plane
      operator: Exists
      effect: NoSchedule
~~~~

The node selector places the controller on the kind control-plane node, where
the host port mapping is configured. The toleration lets it run on that node.
The ClusterIP Service avoids adding a second host exposure path.

Install the pinned chart into a dedicated namespace:

~~~~sh
helm repo add haproxy-ingress https://haproxy-ingress.github.io/charts
helm repo update

helm --kube-context "$CONTEXT" upgrade --install n42-gateway \
  haproxy-ingress/haproxy-ingress \
  --namespace n42-gateway-system \
  --create-namespace \
  --version 0.16.3 \
  --values n42-gateway-values.yaml
~~~~

Wait for the controller and confirm it is scheduled on the control-plane node:

~~~~sh
kubectl --context "$CONTEXT" -n n42-gateway-system rollout status \
  daemonset/n42-gateway-haproxy-ingress
kubectl --context "$CONTEXT" -n n42-gateway-system get pods -o wide
~~~~

If the DaemonSet name differs in the installed chart, use the name shown by
kubectl get daemonsets -n n42-gateway-system.

### 4. Add a GatewayClass, Gateway, and sample application route

For this first lab, keep the Gateway and sample app in the same namespace.
The GatewayClass is cluster-scoped. The app resources are namespaced, so a
later app can add its own route without changing the Helm release.

Save as gateway-demo.yaml:

~~~~yaml
apiVersion: v1
kind: Namespace
metadata:
  name: gateway-demo
---
apiVersion: gateway.networking.k8s.io/v1
kind: GatewayClass
metadata:
  name: haproxy
spec:
  controllerName: haproxy-ingress.github.io/controller
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: echo
  namespace: gateway-demo
spec:
  replicas: 1
  selector:
    matchLabels:
      app: echo
  template:
    metadata:
      labels:
        app: echo
    spec:
      containers:
        - name: agnhost
          image: registry.k8s.io/e2e-test-images/agnhost:2.53
          args:
            - serve-hostname
            - --port=8080
          ports:
            - name: http
              containerPort: 8080
---
apiVersion: v1
kind: Service
metadata:
  name: echo
  namespace: gateway-demo
spec:
  selector:
    app: echo
  ports:
    - name: http
      port: 8080
      targetPort: http
---
apiVersion: gateway.networking.k8s.io/v1
kind: Gateway
metadata:
  name: developer-gateway
  namespace: gateway-demo
spec:
  gatewayClassName: haproxy
  listeners:
    - name: http
      port: 80
      protocol: HTTP
---
apiVersion: gateway.networking.k8s.io/v1
kind: HTTPRoute
metadata:
  name: echo
  namespace: gateway-demo
spec:
  parentRefs:
    - name: developer-gateway
  hostnames:
    - echo.local
  rules:
    - backendRefs:
        - name: echo
          port: 8080
~~~~

Apply and check the workload:

~~~~sh
kubectl --context "$CONTEXT" apply -f gateway-demo.yaml
kubectl --context "$CONTEXT" -n gateway-demo rollout status deployment/echo
kubectl --context "$CONTEXT" -n gateway-demo get gateway,httproute
~~~~

### 5. Send a request through the Gateway

The host port is bound to 127.0.0.1. Send the route hostname as the HTTP
Host header:

~~~~sh
curl --fail --show-error -H 'Host: echo.local' http://127.0.0.1:8080/
~~~~

The response should contain the echo Pod's hostname. N42 Gateway v0.16 does
not report Gateway API resource status, so use a successful HTTP response,
controller logs, and the running Pod as the verification signals.

## Security and Production Considerations

- This is a local HTTP-only lab. Do not expose these host ports to an
  untrusted network.
- The controller runs on the control-plane node only because kind maps host
  ports there. This is suitable for a developer lab, not high availability.
- N42 Gateway v0.16 partially implements Gateway API. It does not implement
  all listener, route filter, or status behavior. Check its current
  [Gateway API notes](https://github.com/n42-gateway/n42-gateway/blob/release-0.16/docs/content/en/docs/configuration/gateway-api.md)
  before using features beyond this example.
- TLS, cert-manager, cross-namespace routing, and application-specific Helm
  releases are outside this first setup. Add them as separate changes after
  validating the plain HTTP path.

## Troubleshooting

| Symptom | Check |
| --- | --- |
| Helm pod is pending | Confirm the control-plane node has the expected label and the values include its toleration. |
| Host port refuses the connection | Check the kind port mapping, controller Pod placement, and DaemonSet readiness. |
| HTTP 404 or no echo response | Check the Service endpoints, GatewayClass controller name, Gateway listener, HTTPRoute hostname, and controller logs. |
| Gateway status is empty | This is expected with N42 Gateway v0.16; validate with a request and controller logs. |
| Gateway API resources are unknown | Confirm the Standard CRDs installed and the controller restarted after CRD installation. |

## Cleanup

Remove the demo resources, controller, and CRDs when you no longer need them:

~~~~sh
kubectl --context "$CONTEXT" delete -f gateway-demo.yaml

helm --kube-context "$CONTEXT" uninstall n42-gateway \
  --namespace n42-gateway-system
kubectl --context "$CONTEXT" delete namespace n42-gateway-system

kubectl --context "$CONTEXT" delete -f \
  https://github.com/kubernetes-sigs/gateway-api/releases/download/v1.7.0/standard-install.yaml
~~~~

Deleting the CRDs removes all Gateway API custom resources in this cluster.
Delete them only if this was the only component using Gateway API.

## Key Takeaways

- Install one shared N42 Gateway controller and Gateway API CRDs.
- Keep the shared controller stable. Let application changes add namespaced
  routes and Services.
- Keep this first lab to HTTP and the stable N42 Gateway v0.16.3 line.
