# System testing preCICE with openfoam-adapter

# Using latest preCICE from dockerhub.com
ARG from=precicecoupling/precice:latest
FROM $from

USER root
ENV USER=root
SHELL ["/bin/bash", "-c"]

# Install dependecies
RUN apt-get -qq update && apt-get -qq install \
    software-properties-common \
    wget apt-transport-https \
    libyaml-cpp-dev

# Installing OpenFOAM 5
RUN sh -c "wget -O - http://dl.openfoam.org/gpg.key | apt-key add -" && \
    add-apt-repository http://dl.openfoam.org/ubuntu && apt update && \
    apt-get -qq -y --no-install-recommends install openfoam5

# Rebuild image if force_rebuild after that command
ARG CACHEBUST

# Building openfoam-adapter
WORKDIR /
RUN git clone https://github.com/precice/openfoam-adapter.git
WORKDIR /openfoam-adapter
RUN source /opt/openfoam5/etc/bashrc && ./Allwmake

# Simulating
WORKDIR /openfoam-adapter/tutorials/CHT/flow-over-plate/buoyantPimpleFoam-laplacianFoam
RUN source /opt/openfoam5/etc/bashrc; ./Allrun

# Copying output files to a folder for further examination
WORKDIR /
RUN mkdir Output && \
    cp -r /openfoam-adapter/tutorials/CHT/flow-over-plate/buoyantPimpleFoam-laplacianFoam/Solid /Output/ && \
    cp -r /openfoam-adapter/tutorials/CHT/flow-over-plate/buoyantPimpleFoam-laplacianFoam/Fluid /Output/
