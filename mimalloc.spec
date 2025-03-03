# TODO
# - drop dependency on libatomic from archs that don't require it
#   https://github.com/microsoft/mimalloc/issues/634
#
# Conditional build:
%bcond_without	static_libs	# static library

Summary:	Compact general purpose allocator with excellent performance
Summary(pl.UTF-8):	Mały alokator pamięci ogólnego przeznaczenia, o dobrej wydajności
Name:		mimalloc
Version:	2.1.9
Release:	1
License:	MIT
Group:		Libraries
Source0:	https://github.com/microsoft/mimalloc/archive/v%{version}/%{name}-%{version}.tar.gz
# Source0-md5:	1b33c11a8f9ea4b7ae0862070892206e
Patch0:		%{name}-build_type.patch
URL:		https://github.com/microsoft/mimalloc
BuildRequires:	cmake >= 3.18
BuildRequires:	libatomic-devel
BuildRequires:	libstdc++-devel >= 6:5
BuildRequires:	rpmbuild(macros) >= 2.007
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
mimalloc (pronounced "me-malloc") is a general purpose allocator with
excellent performance characteristics. Initially developed by Daan
Leijen for the run-time systems of the Koka and Lean languages.
Notable aspects of the design include:
- small and consistent
- free list sharding
- free list multi-sharding
- eager page reset: when a "page" becomes empty (with increased chance
  due to free list sharding) the memory is marked to the OS as unused
  ("reset" or "purged") reducing (real) memory pressure and
  fragmentation, especially in long running programs.
- secure: mimalloc can be built in secure mode
- first-class heaps
- bounded
- fast

%description
mimalloc (wymawiane jak "me-malloc") to alokator pamięci ogólnego
przeznaczenia, o dobrej charakterystyce wydajności. Pierwotnie został
napisany przez Daana Leijena dla systemów uruchomieniowych języków
Koka i Lean. Główne aspekty projektu to:
- mały rozmiar i spójność
- rozdrobnienie list wolnego miejsca
- wielokrotne rozdrobnienie list wolnego miejsca
- oznaczanie wolnych stron jako nie używanych
- bezpieczeństwo (można zbudować w trybie zorientowanym na
  bezpieczeństwo)
- sterty pierwszego poziomu
- ograniczenie najgorszych przypadków
- szybkość

%package devel
Summary:	Header files for the mimalloc library
Summary(pl.UTF-8):	Pliki nagłówkowe biblioteki mimalloc
Group:		Development/Libraries
Requires:	%{name} = %{version}-%{release}
Requires:	libatomic-devel

%description devel
Header files for mimalloc library.

%description devel -l pl.UTF-8
Pliki nagłówkowe biblioteki mimalloc.

%package static
Summary:	Static mimalloc library
Summary(pl.UTF-8):	Statyczna biblioteka mimalloc
Group:		Development/Libraries
Requires:	%{name}-devel = %{version}-%{release}

%description static
Static mimalloc library.

%description static -l pl.UTF-8
Statyczna biblioteka mimalloc.

%prep
%setup -q
%patch -P0 -p1

%build
%cmake -B build \
	-DMI_BUILD_OBJECT:BOOL=OFF \
	%{cmake_on_off static_libs MI_BUILD_STATIC} \
	-DMI_INSTALL_TOPLEVEL:BOOL=ON \
	-DMI_OPT_ARCH:BOOL=OFF

%{__make} -C build

%install
rm -rf $RPM_BUILD_ROOT

%{__make} -C build install \
	DESTDIR=$RPM_BUILD_ROOT

%clean
rm -rf $RPM_BUILD_ROOT

%post	-p /sbin/ldconfig
%postun	-p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libmimalloc.so.*.*
%attr(755,root,root) %ghost %{_libdir}/libmimalloc.so.2

%files devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libmimalloc.so
%{_includedir}/mimalloc.h
%{_includedir}/mimalloc-new-delete.h
%{_includedir}/mimalloc-override.h
%{_libdir}/cmake/mimalloc
%{_pkgconfigdir}/mimalloc.pc

%if %{with static_libs}
%files static
%defattr(644,root,root,755)
%{_libdir}/libmimalloc.a
%endif
