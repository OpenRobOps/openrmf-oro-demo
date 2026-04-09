# syntax=docker/dockerfile:1.4
ARG ROS_DISTRO=jazzy

FROM ghcr.io/open-rmf/rmf/rmf_demos:${ROS_DISTRO}-rmf-latest AS builder

ARG ROS_DISTRO=jazzy
ARG USER=developer
ARG USERID=1000

ENV DEBIAN_FRONTEND=noninteractive
SHELL ["/bin/bash", "-c"]

RUN apt-get update && apt-get install --no-install-recommends -y \
    bash-completion \
    curl \
    git \
    openssh-client \
    python3-colcon-common-extensions \
    python3-pip \
    python3-vcstool \
    python3-rosdep \
    python3-virtualenv \
    rsync \
    software-properties-common \
    sudo \
    tmux \
    unzip \
    vim \
    ros-${ROS_DISTRO}-tf-transformations \
 && rm -rf /var/lib/apt/lists/*

RUN pip install --break-system-packages nudged

RUN rosdep init || true
RUN rosdep update || true

RUN if id -u "${USERID}" >/dev/null 2>&1; then \
      userdel -r "$(getent passwd "${USERID}" | cut -d: -f1)" || true; \
    fi \
 && adduser --uid "${USERID}" --gecos "dev user" --disabled-password "${USER}" \
 && adduser "${USER}" sudo \
 && echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

RUN usermod -a -G dialout,plugdev "${USER}" || true

ENV HOME=/home/${USER}
ENV WS=${HOME}/ws

RUN mkdir -p "${WS}/src" \
 && chown -R "${USER}:${USER}" "${HOME}"

COPY --chown=${USER}:${USER} fleet_adapter/oro.repos ${WS}/oro.repos

RUN --mount=type=ssh,required=true \
    mkdir -p "${WS}/src" /root/.ssh \
 && chmod 700 /root/.ssh \
 && ssh-keyscan github.com >> /root/.ssh/known_hosts \
 && vcs import "${WS}/src" < "${WS}/oro.repos" \
 && chown -R "${USER}:${USER}" "${WS}"

USER ${USER}
WORKDIR ${WS}

RUN echo "export QT_X11_NO_MITSHM=1" >> ${HOME}/.bashrc \
 && echo "source /opt/ros/${ROS_DISTRO}/setup.bash" >> ${HOME}/.bashrc \
 && echo "source /rmf_demos_ws/install/setup.bash" >> ${HOME}/.bashrc \
 && echo "if [ -f ${WS}/install/setup.bash ]; then source ${WS}/install/setup.bash; fi" >> ${HOME}/.bashrc \
 && echo "source /usr/share/colcon_argcomplete/hook/colcon-argcomplete.bash" >> ${HOME}/.bashrc

RUN rosdep update

RUN source /opt/ros/${ROS_DISTRO}/setup.bash \
 && rosdep install --from-paths "${WS}/src" --ignore-src -r -y \
    --skip-keys "rmf_fleet_adapter_python"

RUN source /opt/ros/${ROS_DISTRO}/setup.bash \
 && source /rmf_demos_ws/install/setup.bash \
 && colcon build --symlink-install

COPY fleet_adapter/entrypoint.sh /entrypoint.sh

USER root
RUN chmod +x /entrypoint.sh
USER ${USER}

ENTRYPOINT ["/entrypoint.sh"]