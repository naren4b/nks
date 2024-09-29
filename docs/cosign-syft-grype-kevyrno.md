# 🔐 Enhancing Software Supply Chain Security with Syft and Grype 🛠️

As software producers, we rely on various third-party components and technologies to build and distribute software. Ensuring the security of our entire supply chain has become more critical than ever. That’s where tools like Syft and Grype come into play!

![cosign-image-sumary](https://github.com/user-attachments/assets/01c092e8-fa4f-47f7-8fc1-12d66bae697a)
_A Guide to Generating SBOM with Syft and Grype_

#### In this guide, I walk you through: 
- 1️⃣ Generating SBOMs (Software Bill of Materials) with Syft
- 2️⃣ Scanning for vulnerabilities with Grype
- 3️⃣ Signing images with Cosign for integrity validation
- 4️⃣ Combining SBOM and vulnerability data for a comprehensive view of your software’s security posture.

#### 📌 Key takeaways:
- Understand which components are vulnerable
- Prioritize remediation efforts based on vulnerability severity
- Ensure compliance with security regulations
- Continuously enhance your software’s security

#DevSecOps #CloudSecurity #SoftwareSupplyChain #SBOM #Syft #Grype #Cosign #Containers #Kubernetes #Security #DevOps #SBOMGeneration

💡 Ready to boost your software supply chain security? Check out the detailed guide here:

# Install cosign:
```bash
wget "https://github.com/sigstore/cosign/releases/download/v2.4.0/cosign-linux-amd64" 
sudo mv cosign-linux-amd64 /usr/local/bin/cosign 
sudo chmod +x /usr/local/bin/cosign
```
# Install Syft:
```bash
curl -sSfL https://raw.githubusercontent.com/anchore/syft/main/install.sh | sh -s -- -b /usr/local/bin
```

# Install Grype:
```bash
curl -sSfL https://raw.githubusercontent.com/anchore/grype/main/install.sh | sh -s -- -b /usr/local/bin
```
# Setup your info 
```
export DOCKER_PASSWORD=<password>
export DOCKER_USERNAME=<username>
export IMAGE_NAME=hello-container
export IMAGE_TAG=latest
```
![cosign-image-cicd-process](https://github.com/user-attachments/assets/78154a43-fe91-4df5-8ab4-c7503226fc98)

# Build the docker image
```
cat<<EOF >Dockerfile
FROM nginx:1.27.1
MAINTAINER Narendranath Panda <naren4biz@gmail.com>
COPY static-html-directory /usr/share/nginx/html
EOF

#build
docker build --no-cache linux/amd64 -t $DOCKER_USERNAME/$IMAGE_NAME:$IMAGE_TAG .

# test
docker run --name=$IMAGE_NAME --rm -d --network host  $DOCKER_USERNAME/$IMAGE_NAME:$IMAGE_TAG
curl http://localhost:80

# push 
docker push $DOCKER_USERNAME/$IMAGE_NAME:$IMAGE_TAG
```
# Generate and the cosign signing key and sign the image 
```
cosign generate-key-pair
#cosign sign --key cosign.key docker-username/demo-container
cosign sign --key cosign.key $DOCKER_USERNAME/$IMAGE_NAME:$IMAGE_TAG

#cosign verify --key cosign.pub docker-username/demo-container
cosign verify --key cosign.pub $DOCKER_USERNAME/$IMAGE_NAME:$IMAGE_TAG
```
# Generate the SBOM
```
#If you prefer to receive the output in JSON format, run the following command: 
syft $DOCKER_USERNAME/$IMAGE_NAME:$IMAGE_TAG -o json > $IMAGE_NAME-$IMAGE_TAG-sbom.json

#To extract the package name, version, and license in a tabular format - enabling visibility into all packages and licenses used to create the product, run the following command:

cat $IMAGE_NAME-$IMAGE_TAG.json |  jq -r '.artifacts[] | [.name, .version, (if .licenses == [] then "No license" else [ .licenses[].value ] | join(", ") end)] | @tsv' | awk -F'\t' 'BEGIN {print "Package Name\tPackage Version\tLicense"; print "-------------\t---------------\t-------"} {printf "%s\t%s\t%s\n", $1, $2, $3}'

#To extract the package name, version, and license in a tabular format - enabling visibility into all packages and licenses used to create the product, run the following command:

cat $IMAGE_NAME-$IMAGE_TAG.json | jq '[.artifacts[] | {packageName: .name, packageVersion: .version, license: (if .licenses | length == 0 then "No license" else [ .licenses[].value ] | join(", ") end), locations: [.locations[].path]}]' > packages_with_locations.json

#This may create separate sections for the same Package version and name but with different locations. The following command will unify these sections into one. 
cat $IMAGE_NAME-$IMAGE_TAG.json | jq '[.artifacts[] | {packageName: .name, packageVersion: .version, license: (if .licenses | length == 0 then "No license" else [ .licenses[].value ] | join(", ") end), locations: [.locations[].path]}] | group_by(.packageName + .packageVersion) | map({packageName: .[0].packageName, packageVersion: .[0].packageVersion, license: .[0].license, locations: map(.locations[]) | unique})' > grouped_packages_with_locations.json

cat $IMAGE_NAME-$IMAGE_TAG.json | jq -r '[.artifacts[] | {packageName: .name, packageVersion: .version, license: (if .licenses | length == 0 then "No license" else [ .licenses[].value ] | join(", ") end), locations: [.locations[].path]}] | group_by(.packageName + .packageVersion) | map({packageName: .[0].packageName, packageVersion: .[0].packageVersion, license: .[0].license, locations: map(.locations[]) | unique}) | .[] | [.packageName, .packageVersion, .license, (.locations | join(", "))] | @tsv' | column -t -s $'\t' > grouped_packages_with_locations_tabular.txt

# You can filter by GPL, to focus on packages that typically violate the organization’s policy by running the following command:
cat $IMAGE_NAME-$IMAGE_TAG.json | jq -r '[.artifacts[] | {packageName: .name, packageVersion: .version, license: (if .licenses | length == 0 then "No license" else [ .licenses[].value ] | join(", ") end), locations: [.locations[].path]}] | group_by(.packageName + .packageVersion) | map({packageName: .[0].packageName, packageVersion: .[0].packageVersion, license: .[0].license, locations: map(.locations[]) | unique}) | map(select(.license | test("GPL"))) | .[] | [.packageName, .packageVersion, .license, (.locations | join(", "))] | @tsv' | column -t -s $'\t'> gpl_filtered.json
```

# Generate the Vulnerability
```
#Once you have extracted your SBOM in your preferred format with Syft, Grype will scan the SBOMs to identify and report vulnerabilities, enriching the SBOM with crucial security insights.
grype sbom:sbom.json -o json > $IMAGE_NAME-$IMAGE_TAG-vulnerabilities.json
```
# Combining SBOM and Vulnerability Data
To effectively safeguard your software supply chain, it’s essential to combine insights from SBOMs (Software Bill of Materials) with vulnerability data. This comprehensive approach allows you to better understand the current risk exposure of your technology stack.

Using tools like Syft for generating SBOMs and Grype for vulnerability scanning, we can: 
- ✅ Understand Exposure: Identify vulnerable components and assess their severity. 
- ✅ Prioritize Efforts: Focus on remediating the most critical vulnerabilities. 
- ✅ Ensure Compliance: Keep a clear record of components and vulnerabilities to meet regulatory standards. 
- ✅ Enhance Security Posture: Continuously improve security by regularly scanning and remediating threats.
try the script here [add_vulnerabilities_to_packages.py](https://github.com/naren4b/sbom-gen/blob/main/add_vulnerabilities_to_packages.py)

# Full credit to 🙏 [a-guide-to-generating-sbom-with-syft-and-grype](https://www.jit.io/resources/appsec-tools/a-guide-to-generating-sbom-with-syft-and-grype) 🙏

```bash 
    # Define file paths
    grouped_packages_path = '/path/to/grouped_packages_with_locations.json' # todo $IMAGE_NAME-$IMAGE_TAG-sbom.json
    vulnerabilities_path = '/path/to/vulnerabilities.json' #$IMAGE_NAME-$IMAGE_TAG-vulnerabilities.json
    output_path = '/path/to/final.json'  # todo $IMAGE_NAME-$IMAGE_TAG.json
```
# Sign the SBOM 
```bash 
SHA_ID=$(docker inspect --format='{{.Id}}' $DOCKER_USERNAME/$IMAGE_NAME:$IMAGE_TAG)
cosign sign --key cosign.key $DOCKER_USERNAME/$IMAGE_NAME:$SHA_ID.sbom
```
# What Next 
#### Setup the Kevyrno Policy 
```
```
# Test
```
```
# Ref: 
- https://www.jit.io/resources/appsec-tools/a-guide-to-generating-sbom-with-syft-and-grype
- https://edu.chainguard.dev/open-source/sigstore/policy-controller/how-to-install-policy-controller/
- https://www.docker.com/blog/generate-sboms-with-buildkit/
- https://anchore.com/blog/add-sbom-generation-to-your-github-project-with-syft/
- https://www.youtube.com/watch?v=8GKFzJaEHac&ab_channel=VMwareTanzu
- https://www.youtube.com/watch?v=nybVFJVXbww&ab_channel=Computerphile
- https://edu.chainguard.dev/open-source/sigstore/policy-controller/how-to-install-policy-controller/





