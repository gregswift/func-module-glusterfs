PACKAGE := $(shell basename *.spec .spec)
ARCH = noarch
RPMBUILD = rpmbuild --define "_topdir %(pwd)/rpm-build" \
        --define "_builddir %{_topdir}" \
        --define "_rpmdir %(pwd)/rpms" \
        --define "_srcrpmdir %{_rpmdir}" \
        --define "_sourcedir  %{_topdir}"
VERSION := $(shell awk '/%changelog/ {getline; split($$NF,a,"-"); print a[1]} ' *.spec)
SOURCE = ${PACKAGE}-${VERSION}.tar.gz
PYTHON_SITELIB := $(shell python -c 'from distutils.sysconfig import get_python_lib; print get_python_lib()')

all: rpms

clean:
	-rm -rf ${SOURCE}
	-rm -rf *~
	-rm -rf rpm-build/ rpms/

sdist:
	tar -czf ${SOURCE} modules/

install:
	install -m0644 modules/gluster.py ${PYTHON_SITELIB}/func/minion/modules/

prep_rpmbuild: sdist
	mkdir -p rpm-build
	mkdir -p rpms
	mv ${SOURCE} rpm-build/

rpms: prep_rpmbuild
	${RPMBUILD} -ba ${PACKAGE}.spec

srpm: prep_rpmbuild
	${RPMBUILD} -bs ${PACKAGE}.spec
