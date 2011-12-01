%define build_dkms 1
%{?_with_dkms:%define build_dkms 1}
%{?_without_dkms:%define build_dkms 0}

%define name    ndiswrapper
%define version 1.56
%define release %mkrel 6

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
rm -rf %{buildroot}
install -d %{buildroot}%{_sysconfdir}/%{name}
install -m755 utils/loadndisdriver -D %{buildroot}/sbin/loadndisdriver
install -m755 utils/ndiswrapper -D %{buildroot}%{_sbindir}/ndiswrapper
install -m755 utils/ndiswrapper-buginfo -D %{buildroot}%{_sbindir}/ndiswrapper-buginfo

install -d %{buildroot}%{_mandir}/man8
install -m0644 ndiswrapper.8 %{buildroot}%{_mandir}/man8/

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

install -d -m 755 %{buildroot}%{_sysconfdir}/bash_completion.d
install -m 644 %{SOURCE1} %{buildroot}%{_sysconfdir}/bash_completion.d/ndiswrapper
install -D -m 755 %{SOURCE2} %{buildroot}%{_sysconfdir}/pm/config.d/%{name}

%clean
rm -rf %{buildroot}

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
