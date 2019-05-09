# System testing preCICE with openfoam-adapter

# Using latest preCICE from dockerhub.com
ARG from=precice/precice:latest
FROM $from
ARG SOLVERS_REMOTE

USER root
ENV USER=root

RUN echo "${SOLVERS_REMOTE}"
# Install dependecies
RUN apt-get -qq update && apt-get -qq install \
    software-properties-common \
    wget apt-transport-https \
    libyaml-cpp-dev && \
    rm -rf /var/lib/apt/lists/*

RUN echo "Hi"
## if either we run locally, or we need to update cache on travis
RUN if [ -z "${SOLVERS_REMOTE}" ] || [ ! rsync --list-only "${SOLVERS_REMOTE}/openfoam4" > /dev/null 2>&1 ]; then \
        add-apt-repository "http://dl.openfoam.org/ubuntu dev" && \
        sh -c "wget -O - http://dl.openfoam.org/gpg.key | apt-key add -" && \
        add-apt-repository http://dl.openfoam.org/ubuntu && apt update && \
        apt-get -y install openfoam4 --no-install-recommends && \
        rm -rf /var/lib/apt/lists/*; \
    else \
        # just copy cached version
        rsync -azpvr ${SOLVERS_REMOTE}/openfoam4 /opt/openfoam4 ;\
    fi

# bring back the new version if we run on travis and it has not been cached yet
RUN if [ ! -z "${SOLVERS_REMOTE}" ] && [ ! rsync --list-only "${SOLVERS_REMOTE}/openfoam4" > /dev/null 2>&1 ]; then \
        rsync -azpvr  /opt/openfoam4 ${SOLVERS_REMOTE} ;\
    fi

RUN echo "Haha"
RUN echo "${SOLVERS_REMOTE}"

# Rebuild image if force_rebuild after that command
#ARG CACHEBUST
#
## Building openfoam-adapter
#WORKDIR /
#RUN git clone https://github.com/precice/openfoam-adapter.git
#WORKDIR /openfoam-adapter
#RUN . /opt/openfoam4/etc/bashrc && ./Allwmake
#
## Simulating
#WORKDIR /openfoam-adapter/tutorials/CHT/flow-over-plate/buoyantPimpleFoam-laplacianFoam
#RUN . /opt/openfoam4/etc/bashrc; ./Allrun
#
## Copying output files to a folder for further examination
#WORKDIR /
#RUN mkdir Output && \
#    cp -r /openfoam-adapter/tutorials/CHT/flow-over-plate/buoyantPimpleFoam-laplacianFoam/Solid /Output/ && \
#    cp -r /openfoam-adapter/tutorials/CHT/flow-over-plate/buoyantPimpleFoam-laplacianFoam/Fluid /Output/
