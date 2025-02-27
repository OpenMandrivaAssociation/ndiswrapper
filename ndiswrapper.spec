%bcond_without	dkms

Name: 		ndiswrapper
Version:	1.63
Release:	3
Summary: 	NdisWrapper binary loader utility
License: 	GPL
Group: 		System/Kernel and hardware
URL:		https://ndiswrapper.sourceforge.net/
Source0:	http://prdownloads.sourceforge.net/ndiswrapper/%{name}-%{version}.tar.gz
Source1:	%{name}.bash-completion
Source2:	%{name}.pm-utils
Patch0:  	ndiswrapper-1.59-cflags.patch
Requires: 	kernel

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

%if %{with dkms}
%package -n dkms-%{name}
Summary:	DKMS ndiswrapper module: USUALLY NOT NEEDED
License:	GPL
BuildArch:	noarch
Group:		System/Kernel and hardware
Requires(post,preun): dkms
Requires:	%{name} = %{version}

%description -n dkms-%{name}
** YOU ALMOST CERTAINLY SHOULD NOT INSTALL THIS PACKAGE **. It is only
useful if you are using a kernel with no ndiswrapper module of its own.
All official %{_vendor} kernel packages, and all kernel-tmb packages,
have their own ndiswrapper modules. If you are using one of these
kernels, DO NOT install this package.

DKMS package for %{name} kernel module.
%endif

%prep
%setup -q
%patch0 -p1 -b .cflags

%build
%setup_compile_flags
pushd utils
%make
popd

%install
install -d $RPM_BUILD_ROOT%{_sysconfdir}/%{name}
install -m755 utils/loadndisdriver -D $RPM_BUILD_ROOT/sbin/loadndisdriver
install -m755 utils/ndiswrapper -D $RPM_BUILD_ROOT%{_sbindir}/ndiswrapper
install -m755 utils/ndiswrapper-buginfo -D $RPM_BUILD_ROOT%{_sbindir}/ndiswrapper-buginfo

install -d $RPM_BUILD_ROOT%{_mandir}/man8
install -m0644 ndiswrapper.8 $RPM_BUILD_ROOT%{_mandir}/man8/

%if %{with dkms}
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

%post 
echo -e "please download binary driver (look at http://ndiswrapper.sourceforge.net/)\nuse ndiswrapper -i <inffile.inf> as root to install driver"

%if %{with dkms}
%post -n dkms-%{name}
dkms add -m %{name} -v %{version}-%{release} --rpm_safe_upgrade &&
dkms build -m %{name} -v %{version}-%{release} --rpm_safe_upgrade &&
dkms install -m %{name} -v %{version}-%{release} --rpm_safe_upgrade --force
exit 0

%preun -n dkms-%{name}
dkms remove -m %{name} -v %{version}-%{release} --rpm_safe_upgrade --all
exit 0
%endif

%files
%doc AUTHORS README ChangeLog INSTALL
/sbin/loadndisdriver
%{_sbindir}/ndiswrapper
%{_sbindir}/ndiswrapper-buginfo
%{_sysconfdir}/%{name}
%config(noreplace)%{_sysconfdir}/bash_completion.d/%{name}
%{_sysconfdir}/pm/config.d/%{name}
%{_mandir}/man8/*

%if %{with dkms}
%files -n dkms-%{name}
/usr/src/%{name}-%{version}-%{release}
%endif
