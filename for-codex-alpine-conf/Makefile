VERSION         := 3.20.0

sysconfdir      ?= /etc/lbu

PREFIX          ?=

LIB_FILES       := libalpine.sh dasd-functions.sh

# Core scripts required for a minimal boot environment.
CORE_SBIN_FILES := copy-modloop\
                lbu\
                setup-alpine\
                setup-apkcache\
                setup-apkrepos\
                setup-bootable\
                setup-disk\
                setup-hostname\
                setup-interfaces\
                setup-keymap\
                setup-lbu\
                setup-timezone\
                setup-user\
                update-conf\
                update-kernel

# Additional utilities not required for minimal boot. Maintainers may
# reintroduce them by appending OPTIONAL_SBIN_FILES to SBIN_FILES.
OPTIONAL_SBIN_FILES := setup-acf\
                setup-desktop\
                setup-devd\
                setup-dns\
                setup-mta\
                setup-ntp\
                setup-proxy\
                setup-sshd\
                setup-wayland-base\
                setup-xen-dom0\
                setup-xorg-base

SBIN_FILES      := $(CORE_SBIN_FILES)

BIN_FILES       := uniso

SCRIPTS         := $(LIB_FILES) $(SBIN_FILES)

ETC_LBU_FILES   := lbu.conf
GIT_REV		:= $(shell test -d .git && git describe || echo exported)
ifneq ($(GIT_REV), exported)
FULL_VERSION	:= $(patsubst $(PACKAGE)-%,%,$(GIT_REV))
FULL_VERSION	:= $(patsubst v%,%,$(FULL_VERSION))
else
FULL_VERSION	:= $(VERSION)
endif


DESC="Alpine configuration scripts"
WWW="http://git.alpinelinux.org/cgit/alpine-conf/"


SED		:= sed

SED_REPLACE	:= -e 's:@VERSION@:$(FULL_VERSION):g' \
			-e 's:@PREFIX@:$(PREFIX):g' \
			-e 's:@sysconfdir@:$(sysconfdir):g'

.SUFFIXES:	.sh.in .in
%.sh: %.sh.in
	${SED} ${SED_REPLACE} ${SED_EXTRA} $< > $@

%: %.in
	${SED} ${SED_REPLACE} ${SED_EXTRA} $< > $@ && chmod +x $@

.PHONY:	all apk clean install uninstall iso
all:	$(SCRIPTS) $(BIN_FILES) Kyuafile tests/Kyuafile

uniso:	uniso.c
	$(CC) $(CFLAGS) $(LDFLAGS) -o $@ $^

apk:	$(APKF)

install: $(BIN_FILES) $(SBIN_FILES) $(LIB_FILES) $(ETC_LBU_FILES)
	install -m 755 -d $(DESTDIR)/$(PREFIX)/bin
	install -m 755 $(BIN_FILES) $(DESTDIR)$(PREFIX)/bin
	install -m 755 -d $(DESTDIR)/$(PREFIX)/sbin
	install -m 755 $(SBIN_FILES) $(DESTDIR)/$(PREFIX)/sbin
	install -m 755 -d $(DESTDIR)/$(PREFIX)/lib
	install -m 644 $(LIB_FILES) $(DESTDIR)/$(PREFIX)/lib
	install -m 755 -d $(DESTDIR)/$(sysconfdir)
	install -m 644 $(ETC_LBU_FILES) $(DESTDIR)/$(sysconfdir)

uninstall:
	for i in $(BIN_FILES); do \
		rm -f "$(DESTDIR)/$(PREFIX)/bin/$$i";\
	done
	for i in $(SBIN_FILES); do \
		rm -f "$(DESTDIR)/$(PREFIX)/sbin/$$i";\
	done
	for i in $(LIB_FILES); do \
		rm -f "$(DESTDIR)/$(PREFIX)/lib/$$i";\
	done
	for i in $(ETC_LBU_FILES); do \
		rm -f "$(DESTDIR)/$(sysconfdir)/$$i";\
	done

clean:
	rm -rf $(SCRIPTS) $(BIN_FILES) alpine-conf.iso tests/Kyuafile Kyuafile

alpine-conf.iso: $(SCRIPTS) $(BIN_FILES)
	$(MAKE) install PREFIX=/ DESTDIR=tmp/
	xorriso -as mkisofs -r -V 'ALPINECONF' -J -o $@ tmp/ && rm -rf tmp

iso: alpine-conf.iso

tests/Kyuafile: $(wildcard tests/*_test)
	echo "syntax(2)" > $@
	echo 'test_suite("alpine-conf")' >> $@
	for i in $(notdir $(wildcard tests/*_test)); do \
		echo "atf_test_program{name='$$i',timeout=30}" >> $@ ; \
	done

Kyuafile:
	echo "syntax(2)" > $@
	echo "test_suite('alpine-conf')" >> $@
	echo "include('tests/Kyuafile')" >> $@

check: $(SCRIPTS) $(BIN_FILES) tests/Kyuafile Kyuafile
	kyua --variable parallelism=$(shell nproc) test || (kyua report --verbose && exit 1)

