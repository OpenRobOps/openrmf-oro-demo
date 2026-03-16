# syntax=docker/dockerfile:1

ARG ROS_DISTRO=jazzy

########################################
# Stage 1 - Dev base (tools + user)    #
########################################
FROM ghcr.io/open-rmf/rmf/rmf_demos:${ROS_DISTRO}-rmf-latest AS dev

ARG ROS_DISTRO=jazzy
ARG USER=developer
ARG USERID=1000

ENV DEBIAN_FRONTEND=noninteractive
SHELL ["/bin/bash", "-c"]

# Tools + ROS build essentials
RUN apt-get update && apt-get install --no-install-recommends -y \
    bash-completion \
    curl \
    git \
    python3-colcon-common-extensions \
    python3-pip \
    python3-vcstool \
    python3-rosdep \
    python3-virtualenv \
    software-properties-common \
    sudo \
    tmux \
    unzip \
    vim \
 && rm -rf /var/lib/apt/lists/*

# Python dependency
RUN pip install --break-system-packages nudged

# Make sure rosdep is initialized (some images already have it)
RUN if [ ! -f /etc/ros/rosdep/sources.list.d/20-default.list ]; then \
      rosdep init; \
    fi || true

# Fix RMF workspace permissions (if the folder exists in the image)
RUN if [ -d /rmf_demos_ws ]; then chown -R root:root /rmf_demos_ws; fi

# Create user (delete any existing user with same UID to avoid conflicts)
RUN if id -u "${USERID}" >/dev/null 2>&1; then \
        userdel -r "$(getent passwd ${USERID} | cut -d: -f1)" || true; \
    fi \
 && adduser --uid "${USERID}" --gecos "dev user" --disabled-password "${USER}" \
 && adduser "${USER}" sudo \
 && echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

# Give user ownership of RMF overlay workspace (if present)
RUN if [ -d /rmf_demos_ws ]; then chown -R ${USER}:${USER} /rmf_demos_ws; fi

# Extra groups (optional, but you had them)
RUN usermod -a -G dialout,plugdev ${USER} || true

# Shell init: source ROS + RMF overlay + colcon autocomplete
RUN echo "export QT_X11_NO_MITSHM=1" >> /home/${USER}/.bashrc \
 && echo "source /opt/ros/${ROS_DISTRO}/setup.bash" >> /home/${USER}/.bashrc \
 && echo "if [ -f /rmf_demos_ws/install/setup.bash ]; then source /rmf_demos_ws/install/setup.bash; fi" >> /home/${USER}/.bashrc \
 && echo "source /usr/share/colcon_argcomplete/hook/colcon-argcomplete.bash" >> /home/${USER}/.bashrc

# Optional ROS package you installed
RUN apt-get update && apt-get install --no-install-recommends -y \
    ros-${ROS_DISTRO}-tf-transformations \
 && rm -rf /var/lib/apt/lists/*

# Python deps from your repo
COPY docker/requirements.txt /tmp/requirements.txt
RUN pip install --break-system-packages -r /tmp/requirements.txt

USER ${USER}


########################
# Stage 2 - Build      #
########################
FROM dev AS build

ARG ROS_DISTRO=jazzy
ARG USER=developer

SHELL ["/bin/bash", "-c"]

# Workspace layout
RUN mkdir -p /home/${USER}/ws/src \
 && chown -R ${USER}:${USER} /home/${USER}/ws

# ✅ IMPORTANT: run commands from the workspace root
WORKDIR /home/${USER}/ws

COPY docker/andino.repos /home/${USER}/ws/andino.repos

# Import repos (now "src" exists relative to WORKDIR)
RUN vcs validate < /home/${USER}/ws/andino.repos \
 && vcs import --input /home/${USER}/ws/andino.repos src

# rosdep install
RUN source /opt/ros/${ROS_DISTRO}/setup.bash \
 && if [ -f /rmf_demos_ws/install/setup.bash ]; then source /rmf_demos_ws/install/setup.bash; fi \
 && sudo apt-get update \
 && rosdep update \
 && rosdep install -i -y --rosdistro ${ROS_DISTRO} --from-paths src --ignore-src --skip-keys="gz-sim8" \
 && sudo rm -rf /var/lib/apt/lists/*

# Build Andino workspace (colcon expects src under current dir)
RUN source /opt/ros/${ROS_DISTRO}/setup.bash \
 && if [ -f /rmf_demos_ws/install/setup.bash ]; then source /rmf_demos_ws/install/setup.bash; fi \
 && colcon build --symlink-install --event-handlers console_direct+

RUN mkdir -p /home/${USER}/.inorbit/ \
 && chown -R ${USER}:${USER} /home/${USER}/.inorbit

############################
# Stage 3 - Runtime / final #
############################
FROM build AS andino_slam

ARG ROS_DISTRO=jazzy
ARG USER=developer

SHELL ["/bin/bash", "-c"]

# Entry point
COPY docker/entrypoint.sh /entrypoint.sh
RUN sudo chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]