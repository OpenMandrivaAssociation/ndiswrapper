%define build_dkms 1
%{?_with_dkms:%define build_dkms 1}
%{?_without_dkms:%define build_dkms 0}

%define name    ndiswrapper
%define version 1.47
%define release %mkrel 1

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
Patch:  	ndiswrapper-1.44-cflags.patch
Requires: 	kernel
BuildRoot: 	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

%description
Some vendors refuses to release specs or even a binary 
linux-driver for their WLAN cards. This project tries 
to solve this problem by making a kernel module that 
can load Ndis (windows network driver API) drivers. 
We're not trying to implement all of the Ndis API 
but rather implement the functions needed to get 
these unsupported cards working.

%if %build_dkms
%package -n dkms-%{name}
Summary:	DKMS-ready kernel-source for the ndiswrapper kernel module
License:	GPL
Group:		System/Kernel and hardware
Requires(post,preun): dkms
Requires:	%{name} = %{version}

%description -n dkms-%{name}
DKMS package for %{name} kernel module.
%endif

%prep
%setup -q
%patch -p1 -b .cflags

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
install -D -m 755 %{SOURCE2} $RPM_BUILD_ROOT%{_datadir}/pm-utils/sleep.d/11_ndiswrapper

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
%{_datadir}/pm-utils/sleep.d/11_ndiswrapper
%{_mandir}/man8/*

%if %build_dkms
%files -n dkms-%{name}
%defattr(-,root,root)
/usr/src/%{name}-%{version}-%{release}
%endif

