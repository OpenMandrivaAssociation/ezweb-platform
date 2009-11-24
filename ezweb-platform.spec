%define python_compile_opt python -O -c "import compileall; compileall.compile_dir('.')"
%define python_compile     python -c "import compileall; compileall.compile_dir('.')"

%define ezwebdir %_datadir/%name
%define databasedir %{_localstatedir}/%{_lib}/%name

%define svnrev 2697

Name:		ezweb-platform
Version:	0.1
Release:	%mkrel 0.1.svn%svnrev
# downloaded from svn:
# svn export https://svn.forge.morfeo-project.org/svn/ezwebplatform/ezweb_platform/src/trunk
Source:		ezweb-platform-svn%{svnrev}.tar.bz2
URL:		http://ezweb.morfeo-project.org/
License:	GPLv2+
Group:		System/Servers
Summary:	EzWeb Platform
BuildRoot:      %{_tmppath}/%{name}-buildroot
BuildRequires:	python-devel, python-sqlite, python-django >= 1.0, python-libxml2dom
BuildRequires:	python-psycopg2, python-imaging
Requires:	python-django >= 1.0, apache, apache-mod_python, python-sqlite
Requires:	python-imaging python-libxml2dom
Suggests:	python-psycopg2
BuildArch:	noarch
%description
The EzWeb project is based on the development of key technologies to be
employed in building the front end layer of a new generation SOA
architecture

%prep
%setup -q -n ezweb-platform-svn%{svnrev}
sed -ie "s/^DATABASE_ENGINE = 'postgresql_psycopg2'/DATABASE_ENGINE = 'sqlite3'/" settings.py
sed -ie "s|^DATABASE_NAME = '.*'|DATABASE_NAME = '%{buildroot}%{databasedir}/database'|" settings.py

%build
%python_compile
%python_compile_opt

%install
rm -Rf %{buildroot}

mkdir -p %buildroot%databasedir
touch %{buildroot}%{databasedir}/database

./manage.py syncdb <<EOF
no

EOF
sed -ie "s|^DATABASE_NAME = '.*'|DATABASE_NAME = '%{databasedir}/database'|" settings.py

mkdir -p %{buildroot}%{ezwebdir}
cp -a * %{buildroot}%{ezwebdir}

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
%config(noreplace) %attr(0660,root,apache) %databasedir/database
