ARG centos=stream9-20221206.0
FROM aursu/rpmbuild:${centos}-build

USER root
RUN dnf -y install \
        openssl-devel \
    && dnf clean all && rm -rf /var/cache/dnf

COPY SOURCES ${BUILD_TOPDIR}/SOURCES
COPY SPECS ${BUILD_TOPDIR}/SPECS

RUN chown -R $BUILD_USER ${BUILD_TOPDIR}/{SOURCES,SPECS}

USER $BUILD_USER
ENTRYPOINT ["/usr/bin/rpmbuild", "uw-imap.spec"]
CMD ["-ba"]
