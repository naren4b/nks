# Configure users for your Kubernetes cluster
Trying to give steps for giving access to users to a kubernetes cluster 
![image](https://github.com/naren4b/nks/assets/3488520/80a608b7-0c85-4a24-b6ac-97fca764b354)


```bash
username="${1:-my-user}"
group="${2:-edit}"
expirationSeconds="${3:-86400}"
mkdir ${username}
cd ${username}

```

# Generate a key 
```bash
openssl genrsa -out ${username}.key 2048 
```
# For git-for-windows
```bash
export MSYS_NO_PATHCONV=1
```
# Create the CSR
```bash
openssl req -new -key ${username}.key -out ${username}.csr -subj "/CN=${username}/O=${group}"
```
# Verify the CSR 
```bash
openssl req -in ${username}.csr -noout -text
```
# Create the CertificateSigningRequest
```bash
cat <<EOF >${username}.yaml
apiVersion: certificates.k8s.io/v1
kind: CertificateSigningRequest
metadata:
  name: ${username}
spec:
  request: $(cat ${username}.csr | base64 | tr -d '\n')
  signerName: kubernetes.io/kube-apiserver-client
  expirationSeconds: $expirationSeconds
  usages:
  - client auth
EOF
```
# Check all files are available 
![image](https://github.com/naren4b/nks/assets/3488520/189fc3e4-76a3-413f-85ec-9076e8a56833)


# Approve the CSR
### Connect to your cluster 
```bash
if kubectl config current-context &>/dev/null; then
    current_context=$(kubectl config current-context)
    echo "Connected to Kubernetes cluster using kubeconfig: $kubeconfig_path"
    echo "Current context: $current_context"
else
    echo "Not connected to a Kubernetes cluster using kubeconfig: $kubeconfig_path"
    exit 1
fi

if [ ! -e ${username}.yaml ]; then
    echo "CertificateSigningRequest for ${username}.yaml file does not exist."
fi
```
### Apply and approve the CSR
```bash
kubectl apply -f ${username}.yaml
kubectl certificate approve ${username}
kubectl get csr ${username}  -o jsonpath='{.status.certificate}'| base64 -d > ${username}.crt
```

# Set up the User kubeconfig 
```bash
currentContext=$(kubectl config get-contexts | grep "*" | awk '{print $2}')
currentCluster=$(kubectl config get-contexts | grep "*" | awk '{print $3}')

kubectl config set-credentials ${username} --client-key=${username}.key --client-certificate=${username}.crt --embed-certs=true
kubectl config set-context     ${username} --user=${username} --cluster=${currentCluster}
kubectl config use-context     ${username}
kubectl config view --raw --minify --flatten > ${username}-kubeconfig

kubectl config use-context     ${currentContext}
```

# Setup the RBAC for the user 
```bash
read -p "Choose cluster role [admin, edit, view] " role

echo "This will add ${username} as a ${role} for all namespaces."
read -p "Proceed? [y/N] " confirm

if [[ "${confirm}" != "y" ]]; then
  echo "Aborting"
  exit 0
fi

kubectl create clusterrolebinding ${username}-${role} --user=${username} --clusterrole=${role}
echo list pod -- $(kubectl auth can-i list pod --as ${username})
echo create pod -- $(kubectl auth can-i create pod --as ${username})
echo delete pod -- $(kubectl auth can-i delete pod --as ${username})
```
# Share the details kubeconfig file
```bash
ls -lrt 
```
![image](https://github.com/naren4b/nks/assets/3488520/dde1b35c-c89f-403a-810b-9543a8189dca)

ref: 
- [add-user.sh](https://gist.github.com/naren4b/3df4834e31ae6ad9fb1ce7f65915d12d.js)
- [Doc reference for kubernetes.io](https://kubernetes.io/docs/reference/access-authn-authz/certificate-signing-requests/#approval-rejection-api-client)
- [Demo cluster killercoda.com](https://killercoda.com/playgrounds/scenario/kubernetes)

