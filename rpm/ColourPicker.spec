# sitelib for noarch packages, sitearch for others (remove the unneeded one)
%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")}
%{!?python_sitearch: %global python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print(get_python_lib(1))")}

Name:           ColourPicker
Version:        1.5.0
Release:        1%{?dist}
Summary:        Colour picker

License:        MIT
URL:            https://github.com/stuartlangridge/%{name}
Source0:        https://github.com/stuartlangridge/%{name}/archive/%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  python-devel

%description


%prep
%setup -q


%build
# Remove CFLAGS=... for noarch packages (unneeded)
CFLAGS="$RPM_OPT_FLAGS" %{__python} setup.py build


%install
rm -rf $RPM_BUILD_ROOT
%{__python} setup.py install -O1 --skip-build --root $RPM_BUILD_ROOT

 
%files
%doc
# For noarch packages: sitelib
#%{python_sitelib}/*
/usr/bin/pick-colour-picker
%{python_sitelib}/pick/__init__.py
%{python_sitelib}/pick/__init__.pyc
%{python_sitelib}/pick/__init__.pyo
%{python_sitelib}/pick/__main__.py
%{python_sitelib}/pick/__main__.pyc
%{python_sitelib}/pick/__main__.pyo
%{python_sitelib}/pick_colour_picker-1.0-py2.7.egg-info/PKG-INFO
%{python_sitelib}/pick_colour_picker-1.0-py2.7.egg-info/SOURCES.txt
%{python_sitelib}/pick_colour_picker-1.0-py2.7.egg-info/dependency_links.txt
%{python_sitelib}/pick_colour_picker-1.0-py2.7.egg-info/entry_points.txt
%{python_sitelib}/pick_colour_picker-1.0-py2.7.egg-info/requires.txt
%{python_sitelib}/pick_colour_picker-1.0-py2.7.egg-info/top_level.txt
%{python_sitelib}/pick_colour_picker-1.0-py2.7.egg-info/zip-safe
/usr/share/applications/pick-colour-picker.desktop
/usr/share/icons/hicolor/16x16/apps/pick-colour-picker.png
/usr/share/icons/hicolor/22x22/apps/pick-colour-picker.png
/usr/share/icons/hicolor/24x24/apps/pick-colour-picker.png
/usr/share/icons/hicolor/32x32/apps/pick-colour-picker.png
/usr/share/icons/hicolor/48x48/apps/pick-colour-picker.png
/usr/share/icons/hicolor/512x512/apps/pick-colour-picker.png
/usr/share/icons/hicolor/scalable/apps/pick-colour-picker-symbolic.svg
/usr/share/pixmaps/pick-colour-picker.png
# For arch-specific packages: sitearch
#%{python_sitearch}/*

%changelog
* Tue May 7 2019 Klaatu <klaatu@member.fsf.org> - 1.5.0-1
- Initial RPM spec file
