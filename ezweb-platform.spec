%define python_compile_opt python -O -c "import compileall; compileall.compile_dir('.')"
%define python_compile     python -c "import compileall; compileall.compile_dir('.')"

%define ezwebdir %_datadir/%name
%define databasedir /var/lib/%name

%define svnrev 1525

Name:		ezweb-platform
Version:	0.1
Release:	%mkrel 0.1.svn%svnrev
Source:		ezweb-platform-svn%{svnrev}.tar.bz2
URL:		http://ezweb.morfeo-project.org/
License:	GPLv2+
Group:		System/Servers
Summary:	EzWeb Platform
BuildRoot:      %{_tmppath}/%{name}-buildroot
Requires:	python-django >= 1.0, apache, apache-mod_python, python-sqlite
Requires:	python-psycopg
BuildArch:	noarch
%description
The EzWeb project is based on the development of key technologies to be
employed in building the front end layer of a new generation SOA
architecture

%prep
%setup -q -n ezweb-platform-svn%{svnrev}
sed -ie "s/^DATABASE_ENGINE = 'postgresql'/DATABASE_ENGINE = 'mysql'/" settings.py

%build
%python_compile
%python_compile_opt

%install
rm -Rf %{buildroot}
mkdir -p %{buildroot}%{ezwebdir}
cp -a * %{buildroot}%{ezwebdir}

mkdir -p %buildroot%databasedir

mkdir -p %buildroot%_webappconfdir
cat > %buildroot%_webappconfdir/%name.conf << EOF
  <Location />
    SetHandler python-program
    PythonHandler django.core.handlers.modpython
    SetEnv DJANGO_SETTINGS_MODULE settings

    PythonPath "['/usr/share/ezweb-platform'] + sys.path"
  </Location>

  Alias /media /usr/share/python-support/python-django/django/contrib/admin/media
  Alias /site-media /usr/share/ezweb-platform/media
  Alias /repository /var/www/gadgets
EOF

%post
%_post_webapp

%postun
%_postun_webapp

%files
%defattr(-,root,root)
%config(noreplace) %_webappconfdir/%name.conf
%{ezwebdir}
%attr(0770,root,apache) %databasedir
