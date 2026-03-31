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

RUN pip install --break-system-packages nudged

RUN if [ ! -f /etc/ros/rosdep/sources.list.d/20-default.list ]; then \
      rosdep init; \
    fi || true

RUN if [ -d /rmf_demos_ws ]; then chown -R root:root /rmf_demos_ws; fi

RUN if id -u "${USERID}" >/dev/null 2>&1; then \
        userdel -r "$(getent passwd ${USERID} | cut -d: -f1)" || true; \
    fi \
 && adduser --uid "${USERID}" --gecos "dev user" --disabled-password "${USER}" \
 && adduser "${USER}" sudo \
 && echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

RUN if [ -d /rmf_demos_ws ]; then chown -R ${USER}:${USER} /rmf_demos_ws; fi

RUN usermod -a -G dialout,plugdev ${USER} || true

RUN echo "export QT_X11_NO_MITSHM=1" >> /home/${USER}/.bashrc \
 && echo "source /opt/ros/${ROS_DISTRO}/setup.bash" >> /home/${USER}/.bashrc \
 && echo "if [ -f /rmf_demos_ws/install/setup.bash ]; then source /rmf_demos_ws/install/setup.bash; fi" >> /home/${USER}/.bashrc \
 && echo "if [ -f /home/${USER}/ws/andino_ws/install/setup.bash ]; then source /home/${USER}/ws/andino_ws/install/setup.bash; fi" >> /home/${USER}/.bashrc \
 && echo "source /usr/share/colcon_argcomplete/hook/colcon-argcomplete.bash" >> /home/${USER}/.bashrc

RUN apt-get update && apt-get install --no-install-recommends -y \
    ros-${ROS_DISTRO}-tf-transformations \
 && rm -rf /var/lib/apt/lists/*

USER ${USER}

########################
# Stage 2 - Build      #
########################
FROM dev AS build

ARG ROS_DISTRO=jazzy
ARG USER=developer

SHELL ["/bin/bash", "-c"]

RUN mkdir -p /home/${USER}/ws/andino_ws/src

WORKDIR /home/${USER}/ws/andino_ws

COPY simulation/andino.repos /home/${USER}/ws/andino_ws/andino.repos

RUN mkdir -p src && vcs import src < andino.repos

RUN source /opt/ros/${ROS_DISTRO}/setup.bash \
 && source /rmf_demos_ws/install/setup.bash \
 && sudo apt-get update \
 && rosdep update \
 && rosdep install -i -y --rosdistro ${ROS_DISTRO} --from-paths src --ignore-src --skip-keys="gz-sim8" \
 && sudo rm -rf /var/lib/apt/lists/*

RUN source /opt/ros/${ROS_DISTRO}/setup.bash \
 && source /rmf_demos_ws/install/setup.bash \
 && colcon build \
      --symlink-install \
      --event-handlers console_direct+

RUN mkdir -p /home/${USER}/.inorbit/ \
 && chown -R ${USER}:${USER} /home/${USER}/.inorbit

############################
# Stage 3 - Runtime / final #
############################
FROM build AS andino_slam

ARG ROS_DISTRO=jazzy
ARG USER=developer

SHELL ["/bin/bash", "-c"]

WORKDIR /home/${USER}/ws

COPY simulation/entrypoint.sh /entrypoint.sh
RUN sudo chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]