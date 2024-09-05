# Access kube-api server by curl 
NS=kube-system
kubectl config set-context --current --namespace=$NS

```bash
kubectl create serviceaccount api-explorer
cat<<EOF > api-explorer.yaml
kind: ClusterRole
apiVersion: rbac.authorization.k8s.io/v1beta1
metadata:
  name: log-reader
rules:
- apiGroups: [""] # "" indicates the core API group
  resources: ["pods", "pods/log"]
  verbs: ["get", "watch", "list"]
EOF
kubectl apply -f api-explorer.yaml
kubectl create rolebinding api-explorer:log-reader --clusterrole log-reader --serviceaccount $NS:api-explorer

SERVICE_ACCOUNT=api-explorer

# Get the ServiceAccount's token Secret's name
SECRET=$(kubectl get serviceaccount ${SERVICE_ACCOUNT} -o json | jq -Mr '.secrets[].name | select(contains("token"))')

# Extract the Bearer token from the Secret and decode
TOKEN_B64=$(kubectl get secret ${SECRET} -o json | jq -Mr '.data.token')
TOKEN=$(echo $TOKEN_B64 | base64 -d)

# Extract, decode and write the ca.crt to a temporary location
kubectl get secret ${SECRET} -o json | jq -Mr '.data["ca.crt"]' | base64 -d > /tmp/ca.crt

# Get the API Server location
APISERVER=https://$(kubectl -n default get endpoints kubernetes --no-headers | awk '{ print $2 }')

curl -s $APISERVER/openapi/v2  --header "Authorization: Bearer $TOKEN" --cacert /tmp/ca.crt | less

curl -s $APISERVER/api/v1/namespaces/default/pods/ --header "Authorization: Bearer $TOKEN" --cacert /tmp/ca.crt | jq -rM '.items[].metadata.name'

podName=nginx-5dc7fbd98-hvv6s
curl -s $APISERVER/api/v1/namespaces/default/pods/${podName}/log  --header "Authorization: Bearer $TOKEN" --cacert /tmp/ca.crt

```
