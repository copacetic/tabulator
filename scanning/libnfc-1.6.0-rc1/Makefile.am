ACLOCAL_AMFLAGS = -I m4

AM_CFLAGS = $(LIBNFC_CFLAGS)

SUBDIRS = libnfc utils examples include contrib cmake test

pkgconfigdir = $(libdir)/pkgconfig
pkgconfig_DATA = libnfc.pc

EXTRA_DIST = \
	CMakeLists.txt \
	Doxyfile \
	README-Windows.txt

CLEANFILES = Doxygen.log coverage.info libnfc.pc

clean-local: clean-local-doc clean-local-coverage

.PHONY: clean-local-coverage clean-local-doc doc
clean-local-coverage:
	-rm -rf coverage

clean-local-doc:
	rm -rf doc

doc : Doxyfile
	@DOXYGEN@ $(builddir)/Doxyfile

DISTCHECK_CONFIGURE_FLAGS="--with-drivers=all"

