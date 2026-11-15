# Local Kubernetes with kind

Use [kind](https://kind.sigs.k8s.io/) to run a multi-node Kubernetes cluster
inside Docker. This guide covers the generic cluster setup. Keep application
manifests, ports, ingress settings and workload-specific sizing in the
application's own repository.

> **Version baseline, checked 15 November 2026**
>
> | Component | Version | Notes |
> | --- | --- | --- |
> | kind | `v0.33.0` | Current upstream release |
> | Kubernetes node image | `v1.34.11` | Selected supported image published for kind v0.33.0, pinned by digest below |
> | kubectl | `v1.34.x` | Prefer a matching Kubernetes minor release for this lab |
> | kind config API | `kind.x-k8s.io/v1alpha4` | Current kind cluster config API |
>
> Check the [kind release notes](https://github.com/kubernetes-sigs/kind/releases)
> and [Kubernetes release page](https://kubernetes.io/releases/) before starting
> a new lab. The kind node image does not always use the newest Kubernetes patch.
> This lab intentionally uses Kubernetes v1.34.11 rather than kind's v1.37.0 default.\nUse the exact image and digest published for your kind release.

## 1. Prerequisites

Run these commands in the environment where Docker and kind are installed.
On Windows, a WSL2 distribution with Docker Desktop's WSL integration is one
supported option.

~~~bash
docker version
docker info
kind version
kubectl version --client
~~~

Install kind using its
[official quick start](https://kind.sigs.k8s.io/docs/user/quick-start/).
This guide uses kind `v0.33.0`. For Linux AMD64, including WSL2 on an
`x86_64` host, install that exact release:

~~~bash
curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.33.0/kind-linux-amd64
chmod +x ./kind
sudo install -o root -g root -m 0755 ./kind /usr/local/bin/kind
kind version
~~~

Confirm the output reports `kind v0.33.0`. If more than one copy is installed,
run `type -a kind` and make sure your shell uses the new binary. For other
architectures, use the matching binary listed in the official quick start.

This version matters for the pinned Kubernetes image below. Kubernetes 1.36
and newer use the kubeadm `v1beta4` configuration API. Older kind binaries can
generate a `v1beta3` config that newer node images reject. kind `v0.33.0`
supports the newer API.

The Kubernetes 1.37 API server supports kubectl versions 1.36 through 1.38.
This guide pins `v1.37.1`. Install it on Linux AMD64 and verify its checksum:

~~~bash
curl -LO https://dl.k8s.io/release/v1.37.1/bin/linux/amd64/kubectl
curl -LO https://dl.k8s.io/release/v1.37.1/bin/linux/amd64/kubectl.sha256
echo "$(cat kubectl.sha256)  kubectl" | sha256sum --check
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
kubectl version --client
~~~

For other operating systems and architectures, use the
[Kubernetes install guide](https://kubernetes.io/docs/tasks/tools/).

Confirm Docker is reachable and review existing local clusters before creating
another one:

~~~bash
kind get clusters
kubectl config get-contexts
df -h .
~~~

## 2. Configure a multi-node cluster

This example creates one control-plane node and two worker nodes. It pins the
Kubernetes node image by digest and maps host ports 8080 and 8443 to the
control-plane node. Change the name and ports to fit the lab.

~~~bash
CLUSTER_NAME=dev-cluster
mkdir -p "$CLUSTER_NAME"
cd "$CLUSTER_NAME"

cat > kind-config.yaml <<EOF
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
name: $CLUSTER_NAME
nodes:
- role: control-plane
  image: kindest/node:v1.34.11@sha256:44e222ee2132dab25ff87301682f89eb82c7880ea3a1bf543bfe9708fd08d67d
  extraPortMappings:
  - containerPort: 80
    hostPort: 8080
    listenAddress: "127.0.0.1"
  - containerPort: 443
    hostPort: 8443
    listenAddress: "127.0.0.1"
- role: worker
  image: kindest/node:v1.34.11@sha256:44e222ee2132dab25ff87301682f89eb82c7880ea3a1bf543bfe9708fd08d67d
- role: worker
  image: kindest/node:v1.34.11@sha256:44e222ee2132dab25ff87301682f89eb82c7880ea3a1bf543bfe9708fd08d67d
EOF
~~~

The cluster name is inserted into the YAML when the file is created. Port
mappings only make ports available on the host. An application or ingress controller must still
listen on the mapped container port.

## 3. Create and verify the cluster

Review the config, then create the cluster:

~~~bash
kind create cluster --name "$CLUSTER_NAME" --config kind-config.yaml
kubectl config current-context
kubectl --context "kind-$CLUSTER_NAME" get nodes -o wide
kubectl --context "kind-$CLUSTER_NAME" get storageclass
kubectl --context "kind-$CLUSTER_NAME" get pods -A
~~~

Use the explicit context in lab commands. This avoids sending commands to a
different cluster selected in the current kubeconfig.

kind includes a default local-path StorageClass for disposable local labs.
Confirm it is present before testing a PersistentVolumeClaim. Do not use this
storage as a production durability or backup solution.

## 4. Networking and ingress

This guide does not install an ingress controller. Choose one controller or
Gateway API implementation that is supported by the application stack, then
follow its current official installation guide. Keep its version and values
pinned in the application repository.

The old ingress-nginx installation URL in this guide used the moving `main`
branch. The ingress-nginx project announced retirement after March 2026, so
do not copy that historical install command into a new setup. See the
[project retirement notice](https://github.com/kubernetes/ingress-nginx).

## 5. Load a local application image

Build an image from the application's directory, then load it into this
cluster. Keep the Dockerfile, manifests and image tag with that application.

~~~bash
docker build -t sample-app:0.1.0 .
kind load docker-image sample-app:0.1.0 --name "$CLUSTER_NAME"
~~~

Set the Pod's `imagePullPolicy` to `IfNotPresent` (or `Never`) when using a
locally loaded image, so Kubernetes does not try to pull it from a registry.

## 6. Remove the cluster

Confirm the cluster name and any data you need to keep, then delete the cluster:

~~~bash
kind delete cluster --name "$CLUSTER_NAME"
kind get clusters
~~~

This deletes the cluster's node containers and local cluster data. It does not
delete unrelated Docker resources.

## Repository ownership

This NKS guide covers generic kind installation, configuration, networking,
storage and lifecycle. Put application-specific cluster YAML, resource sizing,
port mappings, ingress settings, certificates and deployment steps in the
owning application or learning repository.

## References

- [kind documentation](https://kind.sigs.k8s.io/docs/)
- [kind releases and supported node images](https://github.com/kubernetes-sigs/kind/releases)
- [kind configuration reference](https://kind.sigs.k8s.io/docs/user/configuration/)
- [Kubernetes release status](https://kubernetes.io/releases/)
- [kubectl install guide](https://kubernetes.io/docs/tasks/tools/)
- [Local Path Provisioner](https://github.com/rancher/local-path-provisioner)
