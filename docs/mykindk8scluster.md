# Get an Linux Instance 
#### Login to the system  
```
ssh -i <pem-file> root@cluster-ip
```
#### Add user  
```
useradd -m -p "${yoursecretpassword}" -d /home/${name}/ -s /bin/bash -G sudo ${name}
PS1='${debian_chroot:+($debian_chroot)}\[\033[01;32m\]\u@\h\[\033[00m\]:\[\033[01;34m\]\w\[\033[00m\]\$ '
```
#### Update the system
```
apt update -y
```
#### Install docker 
```
apt install docker.io
```
#### Install helm
```
curl -fsSL -o get_helm.sh https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3
chmod 700 get_helm.sh
./get_helm.sh
```

#### Install Kubectl
```
curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
curl -LO "https://dl.k8s.io/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl.sha256"
echo "$(<kubectl.sha256) kubectl" | sha256sum --check
sudo install -o root -g root -m 0755 kubectl /usr/local/bin/kubectl
sudo apt install bash-completion -y
source <(kubectl completion bash) # setup autocomplete in bash into the current shell, bash-completion package should be installed first.
echo "source <(kubectl completion bash)" >> ~/.bashrc # add autocomplete permanently to your bash shell.
alias k=kubectl
complete -F __start_kubectl k
```

#### Install Kind
```
curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.11.1/kind-linux-amd64
chmod +x ./kind
mv ./kind /usr/local/bin/kind
```

#### Install cluster 
```
KIND_CLUSTER_NAME=demo
KIND_NODE_VERSION=v1.26.0

cat > config.sh <<EOF
#!/bin/sh

KIND_CLUSTER_NAME=$KIND_CLUSTER_NAME
KIND_NODE_VERSION=$KIND_NODE_VERSION
reg_name='kind-registry'
reg_port='5001'
mkdir -p out
EOF
bash install-kind-cluster.sh
```
#### Check Cluster 
```
docker ps 
kubectl cluster-info
kubectl get sc
kubectl get ingressclasses.networking.k8s.io
```
