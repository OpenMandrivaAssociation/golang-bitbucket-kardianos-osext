# If any of the following macros should be set otherwise,
# you can wrap any of them with the following conditions:
# - %%if 0%%{centos} == 7
# - %%if 0%%{?rhel} == 7
# - %%if 0%%{?fedora} == 23
# Or just test for particular distribution:
# - %%if 0%%{centos}
# - %%if 0%%{?rhel}
# - %%if 0%%{?fedora}
#
# Be aware, on centos, both %%rhel and %%centos are set. If you want to test
# rhel specific macros, you can use %%if 0%%{?rhel} && 0%%{?centos} == 0 condition.
# (Don't forget to replace double percentage symbol with single one in order to apply a condition)

# Generate devel rpm
%global with_devel 1
# Build project from bundled dependencies
%global with_bundled 0
# Build with debug info rpm
%global with_debug 0
# Run tests in check section
%global with_check 1
# Generate unit-test rpm
%global with_unit_test 1

%if 0%{?with_debug}
%global _dwz_low_mem_die_limit 0
%else
%global debug_package   %{nil}
%endif


# upstream has moved from bitbucket to github, provide both things

%global project             kardianos
%global repo                osext

# old: https://bitbucket.org/kardianos/osext
%global old_commit          364fb577de68fb646c4cb39cc0e09c887ee16376
%global old_shortcommit     %(c=%{old_commit}; echo ${c:0:12})
%global provider            bitbucket
%global provider_tld        org
%global provider_prefix     %{provider}.%{provider_tld}/%{project}/%{repo}
%global import_path         %{provider_prefix}
%global old_name            golang-%{provider}-%{project}-%{repo}

# new: https://github.com/kardianos/osext
%global commit              9b883c5eb462dd5cb1b0a7a104fe86bc6b9bd391
%global shortcommit         %(c=%{commit}; echo ${c:0:7})
%global new_provider        github
%global new_provider_tld    com
%global new_provider_prefix %{new_provider}.%{new_provider_tld}/%{project}/%{repo}
%global new_import_path     %{new_provider_prefix}
%global new_name            golang-%{new_provider}-%{project}-%{repo}


Name:           %{old_name}
Version:        0
Release:        0.20.git%{shortcommit}%{?dist}
Summary:        Extensions to the standard Go OS package
License:        BSD
URL:            https://%{new_provider_prefix}
Source0:        https://%{provider_prefix}/get/default.tar.bz2
Source1:        https://%{new_provider_prefix}/archive/%{commit}/%{repo}-%{shortcommit}.tar.gz

Patch0:         00-disable-broken-test.patch

# e.g. el6 has ppc64 arch without gcc-go, so EA tag is required
ExclusiveArch:  %{?go_arches:%{go_arches}}%{!?go_arches:%{ix86} x86_64 aarch64 %{arm}}
# If go_compiler is not set to 1, there is no virtual provide. Use golang instead.
BuildRequires:  %{?go_compiler:compiler(go-compiler)}%{!?go_compiler:golang}

%description
%{summary}

This package provides extensions to the standard Go OS package,
including Executable, which returns an absolute path which can
be used to re-invoke the current program, and ExecutableFolder,
which returns the directory containing the same.


%if 0%{?with_devel}
%package        devel
Summary:        %{summary}
BuildArch:      noarch

Provides:       golang(%{import_path}) = %{version}-%{release}

%description devel
%{summary}

This package contains library source intended for
building other packages which use import path with
%{import_path} prefix.


%package     -n %{new_name}-devel
Summary:        %{summary}
BuildArch:      noarch

Provides:       golang(%{new_import_path}) = %{version}-%{release}

%description -n %{new_name}-devel
%{summary}

This package contains library source intended for
building other packages which use import path with
%{new_import_path} prefix.
%endif


%if 0%{?with_unit_test} && 0%{?with_devel}
%package        unit-test
Summary:        Unit tests for %{old_name} package

# test subpackage tests code from devel subpackage
Requires:       %{old_name}-devel = %{version}-%{release}

%description    unit-test
%{summary}

This package contains unit tests for project
providing packages with %{import_path} prefix.


%package     -n %{new_name}-unit-test
Summary:        Unit tests for %{new_name} package

# test subpackage tests code from devel subpackage
Requires:       %{new_name}-devel = %{version}-%{release}

%description -n %{new_name}-unit-test
%{summary}

This package contains unit tests for project
providing packages with %{new_import_path} prefix.
%endif


%prep
%setup -n %{repo}-%{commit} -b1
%patch0 -p1

%setup -n %{project}-%{repo}-%{old_shortcommit} -b0


%build


%install
# source codes for building projects
%if 0%{?with_devel}
install -d -p %{buildroot}/%{gopath}/src/%{import_path}/
echo "%%dir %%{gopath}/src/%%{import_path}/." >> devel.file-list

install -d -p %{buildroot}/%{gopath}/src/%{new_import_path}/
echo "%%dir %%{gopath}/src/%%{new_import_path}/." >> new-devel.file-list

# find all *.go but no *_test.go files and generate devel.file-list
for file in $(find . -iname "*.go" \! -iname "*_test.go") ; do
    echo "%%dir %%{gopath}/src/%%{import_path}/$(dirname $file)" >> devel.file-list
    install -d -p %{buildroot}/%{gopath}/src/%{import_path}/$(dirname $file)
    cp -pav $file %{buildroot}/%{gopath}/src/%{import_path}/$file
    echo "%%{gopath}/src/%%{import_path}/$file" >> devel.file-list
done

pushd ../%{repo}-%{commit}
# find all *.go but no *_test.go files and generate new-devel.file-list
for file in $(find . -iname "*.go" \! -iname "*_test.go") ; do
    echo "%%dir %%{gopath}/src/%%{new_import_path}/$(dirname $file)" >> new-devel.file-list
    install -d -p %{buildroot}/%{gopath}/src/%{new_import_path}/$(dirname $file)
    cp -pav $file %{buildroot}/%{gopath}/src/%{new_import_path}/$file
    echo "%%{gopath}/src/%%{new_import_path}/$file" >> ../%{project}-%{repo}-%{old_shortcommit}/new-devel.file-list
done
popd
%endif

# testing files for this project
%if 0%{?with_unit_test} && 0%{?with_devel}
install -d -p %{buildroot}/%{gopath}/src/%{import_path}/
install -d -p %{buildroot}/%{gopath}/src/%{new_import_path}/

# find all *_test.go files and generate unit-test.file-list
for file in $(find . -iname "*_test.go"); do
    echo "%%dir %%{gopath}/src/%%{import_path}/$(dirname $file)" >> devel.file-list
    install -d -p %{buildroot}/%{gopath}/src/%{import_path}/$(dirname $file)
    cp -pav $file %{buildroot}/%{gopath}/src/%{import_path}/$file
    echo "%%{gopath}/src/%%{import_path}/$file" >> unit-test.file-list

    echo "%%dir %%{gopath}/src/%%{new_import_path}/$(dirname $file)" >> new-devel.file-list
    install -d -p %{buildroot}/%{gopath}/src/%{new_import_path}/$(dirname $file)
    cp -pav $file %{buildroot}/%{gopath}/src/%{new_import_path}/$file
    echo "%%{gopath}/src/%%{new_import_path}/$file" >> new-unit-test.file-list
done

pushd ../%{repo}-%{commit}
for file in $(find . -iname "*_test.go"); do
    echo "%%dir %%{gopath}/src/%%{new_import_path}/$(dirname $file)" >> new-devel.file-list
    install -d -p %{buildroot}/%{gopath}/src/%{new_import_path}/$(dirname $file)
    cp -pav $file %{buildroot}/%{gopath}/src/%{new_import_path}/$file
    echo "%%{gopath}/src/%%{new_import_path}/$file" >> ../%{project}-%{repo}-%{old_shortcommit}/new-unit-test.file-list
done
popd
%endif

%if 0%{?with_devel}
sort -u -o devel.file-list devel.file-list
sort -u -o new-devel.file-list new-devel.file-list
%endif


%check
%if 0%{?with_check} && 0%{?with_unit_test} && 0%{?with_devel}
%if ! 0%{?with_bundled}
export GOPATH=%{buildroot}/%{gopath}:%{gopath}
%else
# No dependency directories so far

export GOPATH=%{buildroot}/%{gopath}:%{gopath}
%endif

%if ! 0%{?gotest:1}
%global gotest go test
%endif

%gotest %{import_path}
%gotest %{new_import_path}
%endif


#define license tag if not already defined
%{!?_licensedir:%global license %doc}


%if 0%{?with_devel}
%files devel -f devel.file-list
%license LICENSE
%dir %{gopath}/src/%{provider}.%{provider_tld}/%{project}

%files -n %{new_name}-devel -f new-devel.file-list
%license LICENSE
%dir %{gopath}/src/%{new_provider}.%{new_provider_tld}/%{project}
%endif


%if 0%{?with_unit_test} && 0%{?with_devel}
%files unit-test -f unit-test.file-list
%license LICENSE

%files -n %{new_name}-unit-test -f new-unit-test.file-list
%license LICENSE
%endif


%changelog
* Fri Jul 13 2018 Fedora Release Engineering <releng@fedoraproject.org> - 0-0.20.git9b883c5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Wed Feb 07 2018 Fedora Release Engineering <releng@fedoraproject.org> - 0-0.19.git9b883c5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Wed Aug 02 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0-0.18.git9b883c5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Wed Jul 26 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0-0.17.git9b883c5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Fri Mar 04 2017 Fabio Valentini <decathorpe@gmail.com> - 0-0.16.git9b883c5
- Disable a broken test that leads to intermittent failures.

* Fri Mar 03 2017 Fabio Valentini <decathorpe@gmail.com> - 0-0.15.git9b883c5
- Upstream has moved to github, use new sources too.
- Provide new import path too.

* Fri Feb 10 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0-0.14.hg364fb577de68
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Sat Dec 17 2016 Jan Chaloupka <jchaloup@redhat.com> - 0-0.13.hg364fb577de68
- Polish the spec file
  related: #1254591

* Thu Jul 21 2016 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0-0.12.hg364fb577de68
- https://fedoraproject.org/wiki/Changes/golang1.7

* Mon Feb 22 2016 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0-0.11.hg364fb577de68
- https://fedoraproject.org/wiki/Changes/golang1.6

* Wed Feb 03 2016 Fedora Release Engineering <releng@fedoraproject.org> - 0-0.10.hg364fb577de68
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Sat Sep 12 2015 jchaloup <jchaloup@redhat.com> - 0-0.9.hg364fb577de68
- Define gotest macro if not defined

* Fri Sep 11 2015 jchaloup <jchaloup@redhat.com> - 0-0.8.hg364fb577de68
- Update to spec-2.1

* Wed Aug 12 2015 Fridolin Pokorny <fpokorny@redhat.com> - 0-0.7.hg364fb577de68
- Update spec file to spec-2.0
  resolves: #1254591

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0-0.6.hg364fb577de68
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0-0.5.hg364fb577de68
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Wed Oct 16 2013 Lokesh Mandvekar <lsm5@redhat.com> 0-0.4.hg364fb577de68
- removed double quotes from provides

* Mon Oct 14 2013 Lokesh Mandvekar <lsm5@redhat.com> 0-0.3.hg364fb577de68
- devel description update

* Mon Oct 14 2013 Lokesh Mandvekar <lsm5@redhat.com> 0-0.2.hg364fb577de68
- defattr removed
- description and summary updated

* Sat Oct 12 2013 Lokesh Mandvekar <lsm5@redhat.com> 0-0.1.hg364fb577de68
- Initial fedora package

