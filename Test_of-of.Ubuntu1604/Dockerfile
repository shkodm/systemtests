# System testing preCICE with openfoam-adapter

# Using latest preCICE from dockerhub.com
ARG from=precice/precice:latest
FROM $from

USER root
ENV USER=root

ARG DEPS_REMOTE
ENV DEPS_REMOTE=${DEPS_REMOTE}

ARG CCACHE_REMOTE
ENV CCACHE_REMOTE=${CCACHE_REMOTE}

# Install dependecies
RUN apt-get -qq update && apt-get -qq install \
    software-properties-common \
    wget apt-transport-https \
    libyaml-cpp-dev && \
    rm -rf /var/lib/apt/lists/*

# Installing OpenFOAM 4.1
RUN bash /home/pre_install_hook.sh --dep=openfoam4 --prefix="/opt/" && \
    add-apt-repository "http://dl.openfoam.org/ubuntu dev" \
    && sh -c "wget -O - http://dl.openfoam.org/gpg.key | apt-key add -" \
    && add-apt-repository http://dl.openfoam.org/ubuntu && apt update \
    && apt-get -y install openfoam4 --no-install-recommends && \
    bash /home/post_install_hook.sh --dep=openfoam4 --prefix="/opt/" ; return 0 && \
    rm -rf /var/lib/apt/lists/*

# Rebuild image if force_rebuild after that command
ARG CACHEBUST

# Building openfoam-adapter
WORKDIR /
RUN git clone https://github.com/precice/openfoam-adapter.git
WORKDIR /openfoam-adapter
RUN . /opt/openfoam4/etc/bashrc && ./Allwmake

# Simulating
WORKDIR /openfoam-adapter/tutorials/CHT/flow-over-plate/buoyantPimpleFoam-laplacianFoam
RUN . /opt/openfoam4/etc/bashrc; ./Allrun

# Copying output files to a folder for further examination
WORKDIR /
RUN mkdir Output && \
    cp -r /openfoam-adapter/tutorials/CHT/flow-over-plate/buoyantPimpleFoam-laplacianFoam/Solid /Output/ && \
    cp -r /openfoam-adapter/tutorials/CHT/flow-over-plate/buoyantPimpleFoam-laplacianFoam/Fluid /Output/
