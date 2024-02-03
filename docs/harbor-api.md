# Accessing Harbor registry through REST API
Install the registry ref: [Setting up Basic Harbor Registry in a Kubernetes Cluster](basic-harbor-registry.md)

# 01. Setup 
```bash
# check and change these values if needed
cat<< EOF > config.sh
export HARBOR_URL="registry.127.0.0.1.nip.io"
export ADMIN_USER=admin
export ADMIN_PASSWORD="Harbor12345"
OUTDIR=$PWD/out
EOF
source config.sh
```
### Getting stats about the registry 
```bash
rm -rf $PWD/out
export HARBOR_URL=registry.127.0.0.1.nip.io
git clone https://github.com/naren4b/harbor-registry.git
cd harbor-registry/harbor-api
bash 01_getProjects.sh
cp out/projects.txt .
bash run.sh projects.txt
```

### 02. Create a Project 
```bash
project=$1 #demo
cat<<EOF >$project.json
{
  "project_name": "$project",
  "public": false,
  "metadata": {
    "public": "false"
  }
}
EOF

curl -k -s \
        -X POST \
        -u ${ADMIN_USER}:${ADMIN_PASSWORD} \
        -H 'accept: application/json' \
        -H 'Content-Type: application/json' \
        "https://${HARBOR_URL}/api/v2.0/projects" \
        -d @$project.json

docker login $HARBOR_URL -u $ADMIN_USER -p $ADMIN_PASSWORD
docker pull nginx:latest
docker tag nginx:latest $HARBOR_URL/library/nginx:latest
docker push $HARBOR_URL/library/nginx:latest

```
### 03. Get Projects in the Harbor Registry  
```bash
page=1
while :; do
    response=$(curl -k -s \
        -X GET \
        -u ${ADMIN_USER}:${ADMIN_PASSWORD} \
        -H 'accept: application/json' \
        "https://${HARBOR_URL}/api/v2.0/projects?page=$page&page_size=100")
    if [[ "$response" == "[]" ]]; then
        break
    fi
    echo $response >>out/projects.json
    page=$((page + 1))
done

echo "Find projects list at out/projects.txt"
cat out/projects.json | jq -r '.[].name' >out/projects.txt
```
### 04. Get Project Repositories in a Project 
```bash
project=$1
echo "Get info for $project"
rm -rf out/$project
mkdir -p out/$project
page=1
while :; do
    response=$(curl -k -s \
        -X GET \
        -u ${ADMIN_USER}:${ADMIN_PASSWORD} \
        -H 'accept: application/json' \
        "https://${HARBOR_URL}/api/v2.0/projects/${project}/repositories?page=$page&page_size=100")
    if [[ "$response" == "[]" ]]; then
        break
    fi
    echo $response >>out/$project/repositories.json
    page=$((page + 1))
done

# cat out/$project/repositories.json | jq .
```
### 05. Get Details of Repository  
```bash
cat out/$1/repositories.json | jq -r '.[].name' >out/repos.txt

while IFS= read -r line; do
    project=$(echo "$line" | cut -d'/' -f1)
    repo=$(echo "$line" | cut -d'/' -f2-)
    echo "$project,$repo" >>out/$1/repositories.csv
done <out/repos.txt
```
### 06. Get Image Details of a repository  
```
file=out/$1/repositories.csv

getRepoDetails() {
    project=$1
    repo=$2
    rm -rf out/$project/$repo
    mkdir -p out/$project/$repo
    page=1
    while :; do
        URL="""https://${HARBOR_URL}/api/v2.0/projects/${project}/repositories/${repo}/artifacts?page_size=100&page=${page}"""
        response=$(curl -k -s \
            -X GET \
            -u ${ADMIN_USER}:${ADMIN_PASSWORD} \
            -H 'accept: application/json' \
            $URL)
        if [[ "$response" == "[]" ]]; then

            break
        fi
        echo $response | jq . >out/$project/$repo/response.json
        cat out/$project/$repo/response.json | jq -r '.[] | "\(.addition_links.build_history.href),\(.tags[0].name),\(.size)"' | sed 's,/additions/build_history,,g' | sed 's,/api/v2.0/projects/,,g' >>out/$HARBOR_URL-size.csv
        cat out/$project/$repo/response.json | jq -r '.[] | "\(.addition_links.build_history.href),\(.tags[0].name),\(.size)"' | sed 's,/additions/build_history,,g' | sed 's,/api/v2.0/projects/,,g' >>out/$project/$repo/size.csv
        page=$((page + 1))
    done
}

if [ -e "$file" ] && [ -s "$file" ]; then
    while IFS=, read -r project repo; do
        echo "Fetching for $project/$repo"
        getRepoDetails $project "${repo//\//%2F}"
    done <"$file"
else
    if [ ! -e "$file" ]; then
        echo "Error: $file does not exist."
    elif [ ! -s "$file" ]; then
        echo "Error: $file is empty."
    fi
fi
```


### 07. Create a remote registry 
```bash
url=REMOTE-Harbor.todo.com
access_key=TODO
access_secret=TODO
cat<<EOF >my-registry.json
{
  "id": 0,
  "url": "demo.goharbor.io",
  "name": "goharbor",
  "credential": {
    "type": "basic",
    "access_key": "$access_key", 
    "access_secret": "$access_secret"
  },
  "type": "harbor",
  "insecure": true,
  "description": "Demo harbor account",
  "status": "string",
  "creation_time": "2024-01-28T02:10:19.389Z",
  "update_time": "2024-01-28T02:10:19.389Z"
}
EOF

curl -k -s \
        -X POST \
        -u ${ADMIN_USER}:${ADMIN_PASSWORD} \
        -H 'accept: application/json' \
        -H 'Content-Type: application/json' \
        "https://${HARBOR_URL}/api/v2.0/registries" \
        -d @my-registry.json

```
