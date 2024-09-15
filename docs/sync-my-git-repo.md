# Sync one git repo to another git repo
```bash
#!/bin/bash

git config --global http.sslVerify false
git config --global advice.detachedHead false

SOURCE_GIT_URL=$1  # format: ${USERID}:${PASSWORD}@${GITURL}/$GROUP
TARGET_GIT_URL=$2  # format: ${GITURL}/$GROUP

sync() {
            REPO_NAME=$1
            REPO_VERSION=$2
            
            echo clone source git ...
            echo 

            git clone https://${SOURCE_GIT_URL}/${REPO_NAME}.git --branch ${REPO_VERSION}  --single-branch
            cd ${REPO_NAME} || exit

            echo push target git ...
            echo 

            git push https://${TARGET_GIT_URL}/${REPO_NAME}.git tag ${REPO_VERSION}
            if [ $? -eq 0 ]; then
                  echo "${REPO_NAME}.git --branch ${REPO_VERSION} pushed to ${TARGET_GIT_URL} ."
            else
                  echo "Push failed."
            fi

      }
sync $3 $4


```
# Run the script & give the userid and password of target git 
```bash
bash syncmygit #SOURCE_GIT_URL $TARGET_GIT_URL $REPO_NAME $REPO_VERSION
```
