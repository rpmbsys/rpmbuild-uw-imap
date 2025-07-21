
# Fedora review: http://bugzilla.redhat.com/166008

%bcond_without devel
# ship static lib, matches default upstream config
# as convenience to users, since our hacked shlib can potentially break
# abi semi-often
%bcond_with    static

Summary: UW Server daemons for IMAP and POP network mail protocols
Name:	 uw-imap
Version: 2007f
Release: 30%{?dist}

# See LICENSE.txt, http://www.apache.org/licenses/LICENSE-2.0
License: ASL 2.0
URL:	 http://www.washington.edu/imap/
# Old (non-latest) releases live at  ftp://ftp.cac.washington.edu/imap/old/
Source0: ftp://ftp.cac.washington.edu/imap/imap-%{version}%{?beta}%{?dev}%{?snap}.tar.gz

%global soname    c-client
%global shlibname lib%{soname}.so.%{somajor}
%global somajor   2007
%global imap_libs lib%{soname}

# FC4+ uses %%_sysconfdir/pki/tls, previous releases used %%_datadir/ssl
%global ssldir  %(if [ -d %{_sysconfdir}/pki/tls ]; then echo "%{_sysconfdir}/pki/tls"; else echo "%{_datadir}/ssl"; fi)

# imap -> uw-imap rename
Obsoletes: imap < 1:%{version}

Patch1: imap-2007-paths.patch
# See http://bugzilla.redhat.com/229781 , http://bugzilla.redhat.com/127271
Patch2: imap-2004a-doc.patch
Patch5: imap-2007e-overflow.patch
Patch9: imap-2007e-shared.patch
Patch10: imap-2007e-authmd5.patch
Patch12: imap-2007f-format-security.patch
Patch13: imap-2007e-poll.patch
Patch14: 1006_openssl1.1_autoverify.patch
Patch15: imap-2007f-ldflags.patch

BuildRequires: make
BuildRequires: gcc

BuildRequires: openssl-devel

Requires: %{imap_libs}%{?_isa} = %{version}-%{release}

%description
The %{name} package provides UW server daemons for both the IMAP (Internet
Message Access Protocol) and POP (Post Office Protocol) mail access
protocols.  The POP protocol uses a "post office" machine to collect
mail for users and allows users to download their mail to their local
machine for reading. The IMAP protocol allows a user to read mail on a
remote machine without downloading it to their local machine.

%package -n %{imap_libs}
Summary: UW C-client mail library
Obsoletes: libc-client2004d < 1:2004d-2
Obsoletes: libc-client2004e < 2004e-2
Obsoletes: libc-client2004g < 2004g-7
Obsoletes: libc-client2006 < 2006k-2
Obsoletes: libc-client2007 < 2007-2

%description -n %{imap_libs}
Provides a common API for accessing mailboxes.

%package devel
Summary: Development tools for programs which will use the UW IMAP library
Requires: %{imap_libs}%{?_isa} = %{version}-%{release}
# imap -> uw-imap rename
Obsoletes: imap-devel < 1:%{version}
%if "%{imap_libs}" == "libc-client"
Obsoletes: libc-client-devel < %{version}-%{release}
Provides:  libc-client-devel = %{version}-%{release}
%else
Conflicts: libc-client-devel < %{version}-%{release}
%endif

%description devel
Contains the header files and libraries for developing programs
which will use the UW C-client common API.

%package static
Summary: UW IMAP static library
Requires: %{name}-devel = %{version}-%{release}
Requires: openssl-devel

%description static
Contains static libraries for developing programs
which will use the UW C-client common API.

%prep
%setup -q -n imap-%{version}%{?dev}%{?snap}

%patch -P 1 -p1 -b .paths
%patch -P 2 -p1 -b .doc
%patch -P 5 -p1 -b .overflow
%patch -P 9 -p1 -b .shared
%patch -P 10 -p1 -b .authmd5
%patch -P 12 -p1 -b .fmt-sec
%patch -P 13 -p1 -b .poll
%patch -P 14 -p1 -b .openssl11
%patch -P 15 -p1 -b .ldflags

%build
# SSL setup, probably legacy-only, but shouldn't hurt -- Rex
export EXTRACFLAGS="$EXTRACFLAGS $(pkg-config --cflags openssl 2>/dev/null)"
# $RPM_OPT_FLAGS
export EXTRACFLAGS="$EXTRACFLAGS -fPIC $RPM_OPT_FLAGS"
# jorton added these, I'll assume he knows what he's doing. :) -- Rex
export EXTRACFLAGS="$EXTRACFLAGS -fno-strict-aliasing"
%if 0%{?fedora} > 4 || 0%{?rhel} > 4
export EXTRACFLAGS="$EXTRACFLAGS -Wno-pointer-sign"
%endif

echo -e "y\ny" | \
make %{?_smp_mflags} slx \
IP=6 \
EXTRACFLAGS="$EXTRACFLAGS" \
EXTRALDFLAGS="$EXTRALDFLAGS $RPM_LD_FLAGS" \
SPECIALS="LOCKPGM=%{_sbindir}/mlock SSLCERTS=%{ssldir}/certs SSLDIR=%{ssldir} SSLINCLUDE=%{_includedir}/openssl SSLKEYS=%{ssldir}/private SSLLIB=%{_libdir}" \
SSLTYPE=unix \
CCLIENTLIB=$(pwd)/c-client/%{shlibname} \
SHLIBBASE=%{soname} \
SHLIBNAME=%{shlibname}

%install
mkdir -p $RPM_BUILD_ROOT%{_libdir}/

%if %{with static}
install -p -m644 ./c-client/c-client.a $RPM_BUILD_ROOT%{_libdir}/
ln -s c-client.a $RPM_BUILD_ROOT%{_libdir}/libc-client.a
%endif

install -p -m755 ./c-client/%{shlibname} $RPM_BUILD_ROOT%{_libdir}/

# %%ghost'd c-client.cf
touch c-client.cf
install -p -m644 -D c-client.cf $RPM_BUILD_ROOT%{_sysconfdir}/c-client.cf

%if %{with devel}
ln -s %{shlibname} $RPM_BUILD_ROOT%{_libdir}/lib%{soname}.so

mkdir -p $RPM_BUILD_ROOT%{_includedir}/imap/
install -m644 ./c-client/*.h $RPM_BUILD_ROOT%{_includedir}/imap/
# Added linkage.c to fix (#34658) <mharris>
install -m644 ./c-client/linkage.c $RPM_BUILD_ROOT%{_includedir}/imap/
install -m644 ./src/osdep/tops-20/shortsym.h $RPM_BUILD_ROOT%{_includedir}/imap/
%endif

%ldconfig_scriptlets -n %{imap_libs}

%files -n %{imap_libs}
%doc LICENSE.txt NOTICE SUPPORT
%doc docs/RELNOTES docs/*.txt
%ghost %config(missingok,noreplace) %{_sysconfdir}/c-client.cf
%{_libdir}/lib%{soname}.so.*

%if %{with devel}
%files devel
%{_includedir}/imap/
%{_libdir}/lib%{soname}.so
%endif

%if %{with static}
%files static
%{_libdir}/c-client.a
%{_libdir}/libc-client.a
%endif

%changelog
* Wed Feb 24 2021 Remi Collet <remi@remirepo.net> - 2007f-30
- drop uw-imap and uw-imap-static and uw-imap-utils
  as only uw-imap-devel and libc-client needed

* Tue Apr 24 2018 Karsten Hopp <karsten@redhat.com> - 2007f-21
- make sure LDFLAGS are used everywhere (rhbz#1541093)

* Tue Feb 20 2018 Remi Collet <remi@remirepo.net> - 2007f-19
- missing BR on C compiler

* Tue Jan 30 2018 Remi Collet <rcollet@redhat.com> - 2007f-18
- fix compatibility with OpenSSL 1.1 rhbz#1540020
  using patch from debian

* Fri Mar 28 2014 Alexander Ursu <aursu@hostopia.com> - 2007f-17
- disabled pop3, imap daemons and utils
- disabled PAM

* Mon Jul 31 2017 Rex Dieter <rdieter@fedoraproject.org> - 2007f-16
- -devel for el7+ too (#1473520)

* Thu Jul 27 2017 Fedora Release Engineering <releng@fedoraproject.org> - 2007f-15
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Tue Jul 11 2017 Rex Dieter <rdieter@fedoraproject.org> - 2007f-14
- .spec cosmetics, %%define -> %%global, drop %%clean
- workaround el6 libc-client WONTFIX brokenness (#736120)
- use compat-openssl10 on f26+ (#1424334)

* Sat Feb 11 2017 Fedora Release Engineering <releng@fedoraproject.org> - 2007f-13
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Thu Jul 28 2016 Joe Orton <jorton@redhat.com> - 2007f-12
- use poll() not select, from Ben Smithusrt via Debian

* Fri Feb 05 2016 Fedora Release Engineering <releng@fedoraproject.org> - 2007f-11
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Fri Jun 19 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2007f-10
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Mon Aug 18 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2007f-9
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Mon Jul 21 2014 Rex Dieter <rdieter@fedoraproject.org> 2007f-8
- move scriptlets near corresponding %%files

* Sun Jun 08 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2007f-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Mon Apr 14 2014 Jaromir Capik <jcapik@redhat.com> - 2007f-6
- Fixing format-security flaws (#1037374)

* Sun Aug 04 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2007f-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Fri Feb 15 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2007f-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Sun Jul 22 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2007f-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Sat Jan 14 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2007f-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Tue Aug 02 2011 Rex Dieter <rdieter@fedoraproject.org> 2007f-1
- imap-2007f

* Mon Jun 13 2011 Rex Dieter <rdieter@fedoraproject.org> 2007e-13
- _with_system_libc_client option (el6+)
- tight deps via %%?_isa
- drop extraneous Requires(post,postun): xinetd

* Mon Feb 07 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2007e-12
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Tue Apr 27 2010 Rex Dieter <rdieter@fedoraproject.org> - 2007e-11
- SSL connection through IPv6 fails (#485860)
- fix SSLDIR, set SSLKEYS

* Wed Sep 16 2009 Tomas Mraz <tmraz@redhat.com> - 2007e-10
- use password-auth common PAM configuration instead of system-auth
  where available

* Mon Aug 31 2009 Rex Dieter <rdieter@fedoraproject.org>
- omit -devel, -static bits in EPEL builds (#518885)

* Fri Aug 21 2009 Tomas Mraz <tmraz@redhat.com> - 2007e-9
- rebuilt with new openssl

* Sun Jul 26 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2007e-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Wed Jul 08 2009 Rex Dieter <rdieter@fedoraproject.org> - 2007e-7
- fix shared.patch to use CFLAGS for osdep.c too

* Tue Jul 07 2009 Rex Dieter <rdieter@fedoraproject.org> - 2007e-6
- build with -fPIC
- rebase patches (patch fuzz=0)

* Wed Feb 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2007e-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Sun Jan 18 2009 Tomas Mraz <tmraz@redhat.com> 2007e-4
- rebuild with new openssl

* Mon Jan 12 2009 Rex Dieter <rdieter@fedoraproject.org> 2007e-3
- main/-utils: +Req: %%imap_libs = %%version-%%release

* Fri Dec 19 2008 Rex Dieter <rdieter@fedoraproject.org> 2007e-1
- imap-2007e

* Fri Oct 31 2008 Rex Dieter <rdieter@fedoraproject.org> 2007d-1
- imap-2007d

* Wed Oct 01 2008 Rex Dieter <rdieter@fedoraproject.org> 2007b-2
- fix build (patch fuzz) (#464985)

* Fri Jun 13 2008 Rex Dieter <rdieter@fedoraproject.org> 2007b-1
- imap-2007b

* Tue May 18 2008 Rex Dieter <rdieter@fedoraproject.org> 2007a1-3
- libc-client: incomplete list of obsoletes (#446240)

* Wed Mar 19 2008 Rex Dieter <rdieter@fedoraproject.org> 2007a1-2
- uw-imap conflicts with cyrus-imapd (#222486)

* Wed Mar 19 2008 Rex Dieter <rdieter@fedoraproject.org> 2007a1-1
- imap-2007a1
- include static lib
- utils: update %%description

* Thu Mar 13 2008 Rex Dieter <rdieter@fedoraproject.org> 2007a-1
- imap-2007a

* Fri Feb 08 2008 Rex Dieter <rdieter@fedoraproject.org> 2007-3
- respin (gcc43)

* Wed Jan 23 2008 Rex Dieter <rdieter@fedoraproject.org> 2007-2
- Obsoletes: libc-client2006 (#429796)
- drop libc-client hacks for parallel-installability, fun while it lasted

* Fri Dec 21 2007 Rex Dieter <rdieter[AT]fedoraproject.org> 2007-1
- imap-2007

* Tue Dec 04 2007 Rex Dieter <rdieter[AT]fedoraproject.org> 2006k-2
- respin for new openssl

* Fri Nov 09 2007 Rex Dieter <rdieter[AT]fedoraproject.org> 2006k-1
- imap-2006k (final)

* Wed Sep 19 2007 Rex Dieter <rdieter[AT]fedoraproject.org> 2006k-0.1.0709171900
- imap-2006k.DEV.SNAP-0709171900

* Tue Aug 21 2007 Joe Orton <jorton@redhat.com> 2006j-3
- fix License

* Tue Jul 17 2007 Rex Dieter <rdieter[AT]fedoraproject.org> 2006j-2
- imap-2006j2

* Mon Jul 09 2007 Rex Dieter <rdieter[AT]fedoraproject.org> 2006j-1
- imap-2006j1

* Wed Jun 13 2007 Rex Dieter <rdieter[AT]fedoraproject.org> 2006i-1
- imap-2006i

* Wed May 09 2007 Rex Dieter <rdieter[AT]fedoraproject.org> 2006h-1
- imap-2006h
- Obsolete pre-merge libc-client pkgs

* Fri Apr 27 2007 Rex Dieter <rdieter[AT]fedoraproject.org> 2006g-3
- imap-2004a-doc.patch (#229781,#127271)

* Mon Apr  2 2007 Joe Orton <jorton@redhat.com> 2006g-2
- use $RPM_OPT_FLAGS during build

* Mon Apr 02 2007 Rex Dieter <rdieter[AT]fedoraproject.org> 2006g-1
- imap-2006g

* Wed Feb 07 2007 Rex Dieter <rdieter[AT]fedoraproject.org> 2006e-3
- Obsoletes: libc-client2004g
- cleanup/simplify c-client.cf handling

* Fri Jan 26 2007 Rex Dieter <rdieter[AT]fedoraproject.org> 2006e-2
- use /etc/profile.d/krb5-devel.sh

* Fri Jan 26 2007 Rex Dieter <rdieter[AT]fedoraproject.org> 2006e-1
- imap-2006e

* Mon Dec 18 2006 Rex Dieter <rdieter[AT]fedoraproject.org> 2006d-1
- imap-2006d (#220121)

* Wed Oct 25 2006 Rex Dieter <rexdieter[AT]users.sf.net> 2006c1-1
- imap-2006c1

* Fri Oct 06 2006 Rex Dieter <rexdieter[AT]users.sf.net> 2006b-1
- imap-2006b
- %%ghost %%config(missingok,noreplace) %%{_sysconfdir}/c-client.cf

* Fri Oct 06 2006 Rex Dieter <rexdieter[AT]users.sf.net> 2006a-6
- omit EOL whitespace from c-client.cf

* Thu Oct 05 2006 Rex Dieter <rexdieter[AT]users.sf.net> 2006a-5
- %%config(noreplace) all xinetd.d/pam.d bits

* Thu Oct 05 2006 Rex Dieter <rexdieter[AT]users.sf.net> 2006a-4
- eek, pam.d/xinet.d bits were all mixed up, fixed.

* Wed Oct 04 2006 Rex Dieter <rexdieter[AT]users.sf.net> 2006a-3
- libc-client: move c-client.cf here
- c-client.cf: +set new-folder-format same-as-inbox

* Wed Oct 04 2006 Rex Dieter <rexdieter[AT]users.sf.net> 2006a-2
- omit mixproto patch (lvn bug #1184)

* Tue Sep 26 2006 Rex Dieter <rexdieter[AT]users.sf.net> 2006a-1
- imap-2006a
- omit static lib (for now, at least)

* Mon Sep 25 2006 Rex Dieter <rexdieter[AT]users.sf.net> 2006-4
- -devel-static: package static lib separately.

* Mon Sep 25 2006 Rex Dieter <rexdieter[AT]users.sf.net> 2006-3
- License: Apache 2.0

* Fri Sep 15 2006 Rex Dieter <rexdieter[AT]users.sf.net> 2006-2
- imap-2006
- change default (CREATEPROTO) driver to mix
- Obsolete old libc-clients

* Tue Aug 29 2006 Rex Dieter <rexdieter[AT]users.sf.net> 2004g-6
- fc6 respin

* Fri Aug 18 2006 Rex Dieter <rexdieter[AT]users.sf.net> 2004g-5
- cleanup, respin for fc6

* Wed Mar 1 2006 Rex Dieter <rexdieter[AT]users.sf.net>
- fc5: gcc/glibc respin

* Thu Nov 17 2005 Rex Dieter <rexdieter[AT]users.sf.net> 2004g-4
- use pam's "include" feature on fc5
- cleanup %%doc handling, remove useless bits

* Thu Nov 17 2005 Rex Dieter <rexdieter[AT]users.sf.net> 2004g-3
- omit trailing whitespace in default c-client.cf

* Wed Nov 16 2005 Rex Dieter <rexdieter[AT]users.sf.net> 2004g-2
- rebuild for new openssl

* Mon Sep 26 2005 Rex Dieter <rexdieter[AT]users.sf.net> 2004g-1
- imap-2004g
- /etc -> %%_sysconfdir
- use %%{?_smp_mflags}

* Mon Aug 15 2005 Rex Dieter <rexdieter[AT]users.sf.net> 2004e-1
- imap-2004e
- rename: imap -> uw-imap (yay, we get to drop the Epoch)
- sslcerts=%%{_sysconfdir}/pki/tls/certs if exists, else /usr/share/ssl/certs

* Fri Apr 29 2005 Rex Dieter <rexdieter[AT]users.sf.net> 1:2004d-1
- 2004d
- imap-libs -> lib%%{soname}%%{version} (ie, libc-client2004d), so we can
  have multiple versions (shared-lib only) installed
- move mlock to -utils.
- revert RFC2301, locks out too many folks where SSL is unavailable

* Thu Apr 28 2005 Rex Dieter <rexdieter[AT]users.sf.net> 1:2004-0.fdr.11.c1
- change default driver from mbox to mbx
- comply with RFC 3501 security: Unencrypted plaintext passwords are prohibited

* Fri Jan 28 2005 Rex Dieter <rexdieter[AT]users.sf.net> 1:2004-0.fdr.10.c1
- imap-2004c1 security release:
  http://www.kb.cert.org/vuls/id/702777

* Thu Jan 20 2005 Rex Dieter <rexdieter[AT]users.sf.net> 1:2004-0.fdr.9.c
- imap2004c
- -utils: dmail,mailutil,tmail
- -libs: include mlock (so it's available for other imap clients, like pine)
- remove extraneous patches
- %%_sysconfigdir/c-client.cf: use to set MailDir (but don't if upgrading from
  an older version (ie, if folks don't want/expect a change in behavior)

* Mon Sep 13 2004 Rex Dieter <rexdieter at sf.net. 1:2004-0.fdr.8.a
- don't use mailsubdir patch (for now)

* Wed Aug 11 2004 Rex Dieter <rexdieter at sf.net> 1:2004-0.fdr.7.a
- mailsubdir patch (default to ~/Mail instead of ~)

* Fri Jul 23 2004 Rex Dieter <rexdieter at sf.net> 1:2004-0.fdr.6.a
- remove Obsoletes/Provides: libc-client (they can, in fact, co-xist)
- -devel: remove O/P: libc-client-devel -> Conflicts: libc-client-devel

* Thu Jul 16 2004 Rex Dieter <rexdieter at sf.net> 1:2004-0.fdr.5.a
- imap2004a

* Tue Jul 13 2004 Rex Dieter <rexdieter at sf.net> 1:2004-0.fdr.4
- -devel: Req: %%{name}-libs

* Tue Jul 13 2004 Rex Dieter <rexdieter at sf.net> 1:2004-0.fdr.3
- previous imap pkgs had Epoch: 1, we need it too.

* Wed Jul 07 2004 Rex Dieter <rexdieter at sf.net> 2004-0.fdr.2
- use %%version as %%somajver (like how openssl does it)

* Wed Jul 07 2004 Rex Dieter <rexdieter at sf.net> 2004-0.fdr.1
- imap-2004
- use mlock, if available.
- Since libc-client is an attrocious name choice, we'll trump it,
  and provide imap, imap-libs, imap-devel instead (redhat bug #120873)

* Wed Apr 07 2004 Kaj J. Niemi <kajtzu@fi.basen.net> 2002e-4
- Use CFLAGS (and RPM_OPT_FLAGS) during the compilation
- Build the .so through gcc instead of directly calling ld

* Fri Mar  5 2004 Joe Orton <jorton@redhat.com> 2002e-3
- install .so with permissions 0755
- make auth_md5.c functions static to avoid symbol conflicts
- remove Epoch: 0

* Tue Mar 02 2004 Kaj J. Niemi <kajtzu@fi.basen.net> 0:2002e-2
- "lnp" already uses RPM_OPT_FLAGS
- have us conflict with imap, imap-devel

* Tue Mar  2 2004 Joe Orton <jorton@redhat.com> 0:2002e-1
- add post/postun, always use -fPIC

* Tue Feb 24 2004 Kaj J. Niemi <kajtzu@fi.basen.net>
- Name change from c-client to libc-client

* Sat Feb 14 2004 Kaj J. Niemi <kajtzu@fi.basen.net> 0:2002e-0.1
- c-client 2002e is based on imap-2002d
- Build shared version, build logic is copied from FreeBSD net/cclient