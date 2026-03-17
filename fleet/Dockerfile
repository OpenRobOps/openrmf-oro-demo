ARG ROS_DISTRO=jazzy

########################################
# Base image                           #
########################################
FROM ghcr.io/open-rmf/rmf/rmf_demos:${ROS_DISTRO}-rmf-latest AS andino_slam

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
    ros-${ROS_DISTRO}-tf-transformations \
 && rm -rf /var/lib/apt/lists/*

# Python dependency
RUN pip install --break-system-packages nudged

# rosdep setup as root
RUN rosdep init || true
RUN rosdep update || true

# Fix RMF workspace permissions if present
RUN if [ -d /rmf_demos_ws ]; then chown -R root:root /rmf_demos_ws; fi

# Create user
RUN if id -u "${USERID}" >/dev/null 2>&1; then \
        userdel -r "$(getent passwd ${USERID} | cut -d: -f1)" || true; \
    fi \
 && adduser --uid "${USERID}" --gecos "dev user" --disabled-password "${USER}" \
 && adduser "${USER}" sudo \
 && echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

RUN usermod -a -G dialout,plugdev ${USER} || true

# Workspace inside the image
ENV WS=/home/${USER}/ws
RUN mkdir -p ${WS}/src \
 && chown -R ${USER}:${USER} /home/${USER}

# Copy repo into image
COPY --chown=${USER}:${USER} fleet/openrmf-oro-adapter ${WS}/src/openrmf-oro-adapter

USER ${USER}
WORKDIR ${WS}

# Shell init
RUN echo "export QT_X11_NO_MITSHM=1" >> /home/${USER}/.bashrc \
 && echo "source /opt/ros/${ROS_DISTRO}/setup.bash" >> /home/${USER}/.bashrc \
 && echo "if [ -f /rmf_demos_ws/install/setup.bash ]; then source /rmf_demos_ws/install/setup.bash; fi" >> /home/${USER}/.bashrc \
 && echo "if [ -f ${WS}/install/setup.bash ]; then source ${WS}/install/setup.bash; fi" >> /home/${USER}/.bashrc \
 && echo "source /usr/share/colcon_argcomplete/hook/colcon-argcomplete.bash" >> /home/${USER}/.bashrc

# rosdep cache for developer user
RUN rosdep update

# Install dependencies from your workspace
RUN source /opt/ros/${ROS_DISTRO}/setup.bash \
 && if [ -f /rmf_demos_ws/install/setup.bash ]; then source /rmf_demos_ws/install/setup.bash; fi \
 && rosdep install --from-paths src --ignore-src -r -y

# Build workspace
RUN source /opt/ros/${ROS_DISTRO}/setup.bash \
 && if [ -f /rmf_demos_ws/install/setup.bash ]; then source /rmf_demos_ws/install/setup.bash; fi \
 && colcon build --symlink-install

# Entry point
COPY fleet/entrypoint.sh /entrypoint.sh
USER root
RUN chmod +x /entrypoint.sh
USER ${USER}

ENTRYPOINT ["/entrypoint.sh"]