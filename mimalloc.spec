# TODO
# - drop dependency on libatomic from archs that don't require it
#   https://github.com/microsoft/mimalloc/issues/634
#
# Conditional build:
%bcond_without	static_libs	# static library

Summary:	Compact general purpose allocator with excellent performance
Name:		mimalloc
Version:	2.1.4
Release:	1
License:	MIT
Group:		Development/Libraries
Source0:	https://github.com/microsoft/mimalloc/archive/v%{version}/%{name}-%{version}.tar.gz
# Source0-md5:	50f2e6e2bf0e92876bedf95cf5444d43
Patch0:		%{name}-build_type.patch
URL:		https://github.com/microsoft/mimalloc
BuildRequires:	cmake >= 3.13
BuildRequires:	libatomic-devel
BuildRequires:	libstdc++-devel >= 6:5
BuildRequires:	rpmbuild(macros) >= 2.007
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
mimalloc (pronounced "me-malloc") is a general purpose allocator with
excellent performance characteristics. Initially developed by Daan
Leijen for the run-time systems of the Koka and Lean languages.
Notable aspects of the design include:

- small and consistent: the library is about 8k LOC using simple and
  consistent data structures. This makes it very suitable to integrate
  and adapt in other projects. For runtime systems it provides hooks for
  a monotonic heartbeat and deferred freeing (for bounded worst-case
  times with reference counting).
- free list sharding: instead of one big free list (per size class) we
  have many smaller lists per "mimalloc page" which reduces
  fragmentation and increases locality -- things that are allocated
  close in time get allocated close in memory. (A mimalloc page contains
  blocks of one size class and is usually 64KiB on a 64-bit system).
- free list multi-sharding: the big idea! Not only do we shard the
  free list per mimalloc page, but for each page we have multiple free
  lists. In particular, there is one list for thread-local free
  operations, and another one for concurrent free operations. Free-ing
  from another thread can now be a single CAS without needing
  sophisticated coordination between threads. Since there will be
  thousands of separate free lists, contention is naturally distributed
  over the heap, and the chance of contending on a single location will
  be low -- this is quite similar to randomized algorithms like skip
  lists where adding a random oracle removes the need for a more complex
  algorithm.
- eager page reset: when a "page" becomes empty (with increased chance
  due to free list sharding) the memory is marked to the OS as unused
  ("reset" or "purged") reducing (real) memory pressure and
  fragmentation, especially in long running programs.
- secure: mimalloc can be built in secure mode, adding guard pages,
  randomized allocation, encrypted free lists, etc. to protect against
  various heap vulnerabilities. The performance penalty is usually
  around 10% on average over our benchmarks.
- first-class heaps: efficiently create and use multiple heaps to
  allocate across different regions. A heap can be destroyed at once
  instead of deallocating each object separately.
- bounded: it does not suffer from blowup, has bounded worst-case
  allocation times (wcat), bounded space overhead (~0.2% meta-data, with
  at most 12.5% waste in allocation sizes), and has no internal points
  of contention using only atomic operations.
- fast: In our benchmarks, mimalloc outperforms other leading
  allocators (jemalloc, tcmalloc, Hoard, etc), and often uses less
  memory. A nice property is that it does consistently well over a wide
  range of benchmarks. There is also good huge OS page support for
  larger server programs.

%package devel
Summary:	Header files for the mimalloc library
Group:		Development/Libraries
Requires:	%{name} = %{version}-%{release}
Requires:	libatomic-devel

%description devel
Header files for mimalloc library.

%package static
Summary:	Static mimalloc library
Group:		Development/Libraries
Requires:	%{name}-devel = %{version}-%{release}

%description static
Static mimalloc library.

%prep
%setup -q
%patch0 -p1

%build
%cmake -B build \
	-DMI_BUILD_OBJECT:BOOL=OFF \
	%{cmake_on_off static_libs MI_BUILD_STATIC} \
	-DMI_INSTALL_TOPLEVEL:BOOL=ON

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
