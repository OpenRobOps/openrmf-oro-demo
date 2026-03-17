#!/bin/bash

# Copyright 2023 Ekumen, Inc.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#
#    * Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in the
#      documentation and/or other materials provided with the distribution.
#
#    * Neither the name of the the copyright holder nor the names of its
#      contributors may be used to endorse or promote products derived from
#      this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

set -e

# Prints information about usage.
function show_help() {
  echo $'\nUsage:\t build.sh [OPTIONS] \n
  Options:\n
  \t-i --image_name\t\t Name of the image to be built (default andino_inorbit_rmf).\n
  Example:\n
  \t./src/andino_inorbit_rmf/docker/build.sh [-i <imageName>]\n
  \t use -i <imageName> to override the default name value.\n'
}

echo "Building the docker image for base development..."

SCRIPT_FOLDER_PATH="$(cd "$(dirname "$0")"; pwd)"
CONTEXT_FOLDER_PATH="$(cd "$(dirname "$0")"; cd .. ; pwd)"

# Parse arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        -i|--image_name) IMAGE_NAME="${2}"; shift ;;
        -h|--help) show_help ; exit 1 ;;
        *) echo "Unknown parameter passed: $1"; exit 1 ;;
    esac
    shift
done

# Update the arguments to default values if needed.
IMAGE_NAME=${IMAGE_NAME:-andino_inorbit_rmf}
DOCKERFILE_PATH=$SCRIPT_FOLDER_PATH/Dockerfile

USERID=$(id -u)
USER=$(whoami)

echo "Building stage dev..."
docker build -t $IMAGE_NAME \
  --file $DOCKERFILE_PATH \
  --build-arg USERID=$USERID \
  --build-arg USER=$USER \
  --target dev \
  $CONTEXT_FOLDER_PATH

echo "Building stage build..."
docker build -t $IMAGE_NAME \
  --file $DOCKERFILE_PATH \
  --build-arg USERID=$USERID \
  --build-arg USER=$USER \
  --target build \
  $CONTEXT_FOLDER_PATH

echo "Building stage andino_slam..."
docker build -t $IMAGE_NAME \
  --file $DOCKERFILE_PATH \
  --build-arg USERID=$USERID \
  --build-arg USER=$USER \
  --target andino_slam \
  $CONTEXT_FOLDER_PATH
