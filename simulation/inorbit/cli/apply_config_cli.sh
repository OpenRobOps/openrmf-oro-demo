# /bin/bash

cd ${HOME}/.inorbit/local/cli
yes | inorbit apply -f datasources.yaml
yes | inorbit apply -f actiondefinition.yaml