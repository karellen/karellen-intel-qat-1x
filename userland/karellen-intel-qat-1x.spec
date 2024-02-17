%global debug_package %{nil}
%global _missing_build_ids_terminate_build 0
%global intel_source QAT.L.4.24.0-00005.tar.gz

%global buildforkernels akmod
%global debug_package %{nil}

# Enable zipping the modules with xz
%global zipmodules 1

%define __spec_install_post \
  %{__arch_install_post}\
  %{__os_install_post}\
  %{__mod_compress_install_post}

%define __mod_compress_install_post \
  if [ "%{zipmodules}" -eq "1" ]; then \
    find %{buildroot}/usr/lib/modules/ -type f -name '*.ko' | xargs xz; \
  fi


Name: karellen-intel-qat-1x
Version: 4.24.0.5
Release: 1
License: ASL 2.0
Summary: Karellen Intel QuickAssist for Linux HW 1.x
Url: https://github.com/karellen/%{name}
Vendor: Karellen, Inc.
Packager: Karellen, Inc. <supervisor@karellen.co>
Group: System Tools
Requires(pre): shadow-utils
ExclusiveArch: x86_64

BuildRequires: make automake autoconf libtool openssl-devel zlib-devel pkg-config
BuildRequires: tar gcc-c++ libnl3-devel nasm kernel-devel-matched systemd-devel pciutils

Requires: libnl3

Source: https://github.com/karellen/karellen-intel-qat-1x/raw/binaries-%{version}/%{intel_source}
Source1: https://github.com/karellen/karellen-intel-qat-1x/raw/binaries-%{version}/kernel-6.7.patch

%description
Karellen Intel QuickAssist for Linux HW 1.x

%package service
Summary: Karellen Intel QAT 1.x service daemon
Requires: %{name}%{?_isa} = %{version}-%{release}
%{?systemd_requires}

%description service
blah

%package devel
Summary: Karellen Intel QAT 1.x development libraries
Requires: %{name}%{?_isa} = %{version}-%{release}

%description devel
blah

%package kmod
Summary: Karellen Intel QAT 1.x kernel modules
Requires: %{name}%{?_isa} = %{version}-%{release}
BuildRequires: kmodtool
%{expand:%(kmodtool --target %{_target_cpu} --kmodname %{name}-kmod %{?buildforkernels:--%{buildforkernels}} %{?kernels:--for-kernels "%{?kernels}"} 2>/dev/null) }

%description kmod
blah

%prep
%autosetup -v
tar -xf %{intel_source}
patch -p0 -l %{SOURCE1}

for kernel_version in %{?kernel_versions} ; do
    cp -a quickassist/qat _kmod_build_${kernel_version%%___*}
done

%build
if [ -z "%{?kernel_versions}" ]; then
  %configure
  make osal_build quickassist-user adf-ctl-all adf-rl-all
fi

for kernel_version in %{?kernel_versions}; do
    make %{?_smp_mflags} -C "${kernel_version##*___}" SUBDIRS=${PWD}/_kmod_build_${kernel_version%%___*}
done

%install
# make DESTDIR=%{buildroot} samples-install
if [ -z "%{?kernel_versions}" ]; then
  mkdir -p %{buildroot}%{_libdir}/
  install build/*.so %{buildroot}%{_libdir}/
  install build/*a %{buildroot}%{_libdir}/
else
  rm -rf ${RPM_BUILD_ROOT}
  for kernel_version in %{?kernel_versions}; do
      make install DESTDIR=${RPM_BUILD_ROOT} KMODPATH=%{kmodinstdir_prefix}/${kernel_version%%___*}/%{kmodinstdir_postfix} ${kernel_version%%___*}/%{kmodinstdir_postfix}/kmodname/
  done
  chmod u+x ${RPM_BUILD_ROOT}/lib/modules/*/extra/*/*
  %{?akmod_install}
fi

%files
%license LICENSE*
%{_libdir}/*


%files devel
%{_libdir}/*.a

%pre
getent group qat >/dev/null || groupadd -r qat
exit 0

%post

%preun

%postun

%changelog
