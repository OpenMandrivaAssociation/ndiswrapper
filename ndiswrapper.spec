%define build_dkms 1
%{?_with_dkms:%define build_dkms 1}
%{?_without_dkms:%define build_dkms 0}

%define name    ndiswrapper
%define version 1.56
%define release %mkrel 8

Name: 		%{name}
Version: 	%{version}
Release: 	%{release}
Summary: 	NdisWrapper binary loader utility
License: 	GPL
Group: 		System/Configuration/Hardware
URL:		http://ndiswrapper.sourceforge.net/
Source0:	http://prdownloads.sourceforge.net/ndiswrapper/%{name}-%{version}.tar.gz
Source1:	%{name}.bash-completion
Source2:	%{name}.pm-utils
Patch0:  	ndiswrapper-1.44-cflags.patch
Patch1:		ndiswrapper-2.6.35-buildfix.patch
Patch2:		ndiswrapper-2.6.36-buildfix.patch
Patch3:		ndiswrapper-2.6.38-buildfix.patch
Requires: 	kernel
%if %{mdkversion} >= 201100
BuildRequires:	rpm-build >= 1:5.3.12
%endif
BuildRoot: 	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

%description
Ndiswrapper implements the Windows kernel APIs within the Linux kernel.  This
allows you to use a Windows driver for a wireless network card. The driver
runs natively, as though it is in Windows, without binary emulation.  This is
not ideal, but is useful when a vendor does not provide Linux drivers and no
free and open driver exists.

With ndiswrapper, most miniPCI (builtin), PCI, PCMCIA (Cardbus only) or USB
wireless network adapteers work in Linux. Although ndiswrapper is intended for
wireless network cards, other devices are known to work, such as ethernet
cards, USB to serial port device, and home phone network devices.

Note that ndiswrapper is known to cause occational computer lockups.

%if %build_dkms
%package -n dkms-%{name}
Summary:	DKMS ndiswrapper module: USUALLY NOT NEEDED
License:	GPL
Group:		System/Kernel and hardware
Requires(post,preun): dkms
Requires:	%{name} = %{version}

%description -n dkms-%{name}
** YOU ALMOST CERTAINLY SHOULD NOT INSTALL THIS PACKAGE **. It is only
useful if you are using a kernel with no ndiswrapper module of its own.
All official Mandriva kernel packages, and all kernel-tmb packages,
have their own ndiswrapper modules. If you are using one of these
kernels, DO NOT install this package.

DKMS package for %{name} kernel module.
%endif

%prep
%setup -q
%patch0 -p1 -b .cflags
%patch1 -p1 -b .buildfix-35
%patch2 -p1 -b .buildfix-36
%patch3 -p1 -b .buildfix-38

%build
pushd utils
CFLAGS="$RPM_OPT_FLAGS" \
%make
popd

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT%{_sysconfdir}/%{name}
install -m755 utils/loadndisdriver -D $RPM_BUILD_ROOT/sbin/loadndisdriver
install -m755 utils/ndiswrapper -D $RPM_BUILD_ROOT%{_sbindir}/ndiswrapper
install -m755 utils/ndiswrapper-buginfo -D $RPM_BUILD_ROOT%{_sbindir}/ndiswrapper-buginfo

install -d $RPM_BUILD_ROOT%{_mandir}/man8
install -m0644 ndiswrapper.8 $RPM_BUILD_ROOT%{_mandir}/man8/

%if %build_dkms
mkdir -p %{buildroot}/usr/src/%{name}-%{version}-%{release}
cp -a driver/* %{buildroot}/usr/src/%{name}-%{version}-%{release}
cat > %{buildroot}/usr/src/%{name}-%{version}-%{release}/dkms.conf <<EOF

PACKAGE_VERSION="%{version}-%{release}"

# Items below here should not have to change with each driver version
PACKAGE_NAME="%{name}"
MAKE[0]="make KVERS=\${kernelver} -C \${dkms_tree}/\${PACKAGE_NAME}/\${PACKAGE_VERSION}/build"
CLEAN="make -C \${kernel_source_dir} SUBDIRS=\${dkms_tree}/\${PACKAGE_NAME}/\${PACKAGE_VERSION}/build clean"

BUILT_MODULE_NAME[0]="\$PACKAGE_NAME"
DEST_MODULE_LOCATION[0]="/kernel/3rdparty/%{name}"
MODULES_CONF_ALIAS_TYPE[0]="eth"

REMAKE_INITRD="no"
AUTOINSTALL=yes
EOF
%endif

install -d -m 755 $RPM_BUILD_ROOT%{_sysconfdir}/bash_completion.d
install -m 644 %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}/bash_completion.d/ndiswrapper
install -D -m 755 %{SOURCE2} $RPM_BUILD_ROOT%{_sysconfdir}/pm/config.d/%{name}

%clean
rm -rf $RPM_BUILD_ROOT

%post 
echo -e "please download binary driver (look at http://ndiswrapper.sourceforge.net/)\nuse ndiswrapper -i <inffile.inf> as root to install driver"

%if %build_dkms
%post -n dkms-%{name}
dkms add -m %{name} -v %{version}-%{release} --rpm_safe_upgrade
dkms build -m %{name} -v %{version}-%{release} --rpm_safe_upgrade
dkms install -m %{name} -v %{version}-%{release} --rpm_safe_upgrade --force
exit 0

%preun -n dkms-%{name}
dkms remove -m %{name} -v %{version}-%{release} --rpm_safe_upgrade --all
exit 0
%endif

%files
%defattr(-,root,root) 
%doc AUTHORS README ChangeLog INSTALL
/sbin/loadndisdriver
%{_sbindir}/ndiswrapper
%{_sbindir}/ndiswrapper-buginfo
%{_sysconfdir}/%{name}
%config(noreplace)%{_sysconfdir}/bash_completion.d/%{name}
%{_sysconfdir}/pm/config.d/%{name}
%{_mandir}/man8/*

%if %build_dkms
%files -n dkms-%{name}
%defattr(-,root,root)
/usr/src/%{name}-%{version}-%{release}
%endif


%changelog
* Mon Jul 04 2011 Per Øyvind Karlsen <peroyvind@mandriva.org> 1.56-6mdv2011.0
+ Revision: 688653
- add versioned buildrequires on rpm-build to get proper kmod() provides

* Fri Jun 24 2011 Franck Bui <franck.bui@mandriva.com> 1.56-5
+ Revision: 686894
- Release 1.56-5
- Build fix for 2.6.38
- Remove BKL from ndiswrapper-2.6.36-buildfix.patch
  BKL wasn't needed by ioctl. See ndiswrapper SVN

* Wed May 04 2011 Oden Eriksson <oeriksson@mandriva.com> 1.56-4
+ Revision: 666604
- mass rebuild

* Sat Oct 02 2010 Thomas Backlund <tmb@mandriva.org> 1.56-3mdv2011.0
+ Revision: 582555
- fix build with 2.6.36 series kernels

* Sat Jul 31 2010 Thomas Backlund <tmb@mandriva.org> 1.56-2mdv2011.0
+ Revision: 563943
- fix build with 2.6.35 series kernels

* Thu Feb 11 2010 Funda Wang <fwang@mandriva.org> 1.56-1mdv2010.1
+ Revision: 504114
- new version 1.56

* Fri Jul 03 2009 Funda Wang <fwang@mandriva.org> 1.55-1mdv2010.0
+ Revision: 391884
- new version 1.55

* Fri May 01 2009 Funda Wang <fwang@mandriva.org> 1.54-1mdv2010.0
+ Revision: 369881
- New version 1.54

* Sat Mar 07 2009 Antoine Ginies <aginies@mandriva.com> 1.53-5mdv2009.1
+ Revision: 351632
- rebuild

* Tue Sep 23 2008 Olivier Blin <oblin@mandriva.com> 1.53-4mdv2009.0
+ Revision: 287632
- use a config file instead of a hook to unload ndiswrapper module in pm-utils
- better fix for sleep.d hook

* Mon Sep 22 2008 Frederic Crozat <fcrozat@mandriva.com> 1.53-3mdv2009.0
+ Revision: 286496
- Update source2 with new location of pm-utils function file (Mdv bug #44004)

* Mon Sep 15 2008 Olivier Blin <oblin@mandriva.com> 1.53-2mdv2009.0
+ Revision: 284839
- adapt to new pm-utils helpers location

  + Austin Acton <austin@mandriva.org>
    - update and tidy description

* Sun Jun 29 2008 Thomas Backlund <tmb@mandriva.org> 1.53-1mdv2009.0
+ Revision: 229996
- update to 1.53

* Tue Jun 17 2008 Thierry Vignaud <tv@mandriva.org> 1.52-3mdv2009.0
+ Revision: 223339
- rebuild

* Thu Mar 20 2008 Adam Williamson <awilliamson@mandriva.org> 1.52-2mdv2008.1
+ Revision: 189197
- add big warnings that most people should not install dkms-ndiswrapper

* Sat Feb 23 2008 Thomas Backlund <tmb@mandriva.org> 1.52-1mdv2008.1
+ Revision: 174048
- update to 1.52

  + Olivier Blin <oblin@mandriva.com>
    - restore BuildRoot

* Mon Dec 31 2007 Thomas Backlund <tmb@mandriva.org> 1.51-1mdv2008.1
+ Revision: 139718
- update to 1.51

  + Thierry Vignaud <tv@mandriva.org>
    - kill re-definition of %%buildroot on Pixel's request

* Wed Dec 05 2007 Funda Wang <fwang@mandriva.org> 1.50-1mdv2008.1
+ Revision: 115543
- update to new version 1.50

* Wed Nov 14 2007 Funda Wang <fwang@mandriva.org> 1.49-2mdv2008.1
+ Revision: 108817
- rebuild for new lzma

* Sun Oct 28 2007 Funda Wang <fwang@mandriva.org> 1.49-1mdv2008.1
+ Revision: 102856
- New version 1.49

* Tue Oct 02 2007 Olivier Blin <oblin@mandriva.com> 1.47-2mdv2008.0
+ Revision: 94484
- update to new version

* Sun Jun 24 2007 Emmanuel Andry <eandry@mandriva.org> 1.47-1mdv2008.0
+ Revision: 43635
- New version

* Fri Jun 01 2007 Herton Ronaldo Krzesinski <herton@mandriva.com.br> 1.44-2mdv2008.0
+ Revision: 34325
- Build ndiswrapperutils using optflags, as reported by Anssi Hannula on
  cooker ML (+ cflags patch).

* Tue May 22 2007 Herton Ronaldo Krzesinski <herton@mandriva.com.br> 1.44-1mdv2008.0
+ Revision: 29858
- Updated to 1.44.
- Removed bogus mdkversion check to define build_dkms (always set to 1).
- Removed duplicated setup of dkms content.
- Updated post message (ndiswrapper website changed, just made a more
  generic message now).
- Updated dkms post/preun scripts: reenabled preun remove, we can do
  this without breaking upgrades now using --force at install on post
  script.


* Fri Mar 23 2007 Olivier Blin <oblin@mandriva.com> 1.21-2mdv2007.1
+ Revision: 148203
- make pm-utils unload ndiswrapper module on suspend (from Adam Pigg, #28554)
- Import ndiswrapper

* Fri Jul 21 2006 Emmanuel Andry <eandry@mandriva.org> 1.21-1mdv2007
- 1.21

* Sun Jul 09 2006 Emmanuel Andry <eandry@mandriva.org> 1.19-2mdv2007
- remove unused patches

* Sun Jul 09 2006 Emmanuel Andry <eandry@mandriva.org> 1.19-1mdv2007
- 1.19
- bzip2 source

* Sat May 20 2006 Arnaud Patard <apatard@mandriva.com> 1.16-1mdk
- 1.16

* Tue Mar 14 2006 Buchan Milne <bgmilne@mandriva.org> 1.6-3mdk
- build dkms subpackage on cooker too

* Sat Mar 11 2006 Oden Eriksson <oeriksson@mandriva.com> 1.6-2mdk
- add the manpage

* Fri Jan 20 2006 Arnaud Patard <apatard@mandriva.com> 1.6-1mdk
- 1.6

* Sat Sep 10 2005 Gwenole Beauchesne <gbeauchesne@mandriva.com> 1.2-3mdk
- check for compatible driver architecture at install time

* Fri Sep 02 2005 Buchan Milne <bgmilne@linux-mandrake.com> 1.2-2mdk
- merge (again) dkms subpackage that was created while package was in between
  repos, build dkms subpackages only for non-cooker
- fix DistroSpecificReleaseTag (will require compat macros for backport)

* Fri Jul 29 2005 Arnaud Patard <apatard@mandriva.com> 1.2-1mdk
- Update to 1.2

* Thu May 19 2005 Olivier Blin <oblin@mandriva.com> 1.2-0.rc1.3mdk
- build with version 1.2rc1 so that it works at least with kernel-mm

* Mon May 09 2005 Guillaume Rousse <guillomovitch@mandriva.org> 1.2- 0.rc1.2 
- bash completion

* Tue Apr 26 2005 Arnaud Patard <apatard@mandrakesoft.com> 1.2-0.rc1.1mdk
- Update to 1.2-rc1.

* Thu Mar 31 2005 Olivier Blin <oblin@mandrakesoft.com> 1.0-3mdk
- Patch0: fix driver installation if its path contains spaces

* Mon Feb 14 2005 Buchan Milne <bgmilne@linux-mandrake.com> 1.0-2mdk
- merge dkms subpackage that was created while package was in main cvs
- fix DistroSpecificReleaseTag (will require compat macros for backport)

* Wed Feb 09 2005 Angelo Naselli <anaselli@mandrake.org> 1.0-1mdk
- 1.0
- added DistroSpecificReleaseTag

* Fri Dec 24 2004 Per Øyvind Karlsen <peroyvind@linux-mandrake.com> 0.12-1mdk
- 0.12
- fix url to list of cards
- cosmetics

* Sat Nov 06 2004 Guillaume Rousse <guillomovitch@mandrake.org> 0.11-1mdk 
- new version
- fixed build

* Sat Aug 07 2004 Per Øyvind Karlsen <peroyvind@linux-mandrake.com> 0.9-1mdk
- 0.9
- cleanups

* Thu Jul 22 2004 Nicolas Planel <nplanel@mandrakesoft.com> 0.8-1mdk
- 0.8.

* Thu May 20 2004 Stew Benedict <sbenedict@mandrakesoft.com> 0.7-5mdk
- try again to drop wlan_radio_averatec_5110hx build on ppc

* Tue May 18 2004 Nicolas Planel <nplanel@mandrakesoft.com> 0.7-4mdk
- add /etc/ndiswrapper directory.
- loadndiswrapper need to be in /sbin path (called from kernel module driver).

* Thu May 13 2004 Stew Benedict <sbenedict@mandrakesoft.com> 0.7-3mdk
- include INSTALL doc with the info on how to setup/install drivers

* Wed May 12 2004 Stew Benedict <sbenedict@mandrakesoft.com> 0.7-2mdk
- drop wlan_radio_averatec_5110hx build on ppc, include the bin otherwise

* Thu Apr 29 2004 Austin Acton <austin@mandrake.org> 0.7-1mdk
- 0.7

