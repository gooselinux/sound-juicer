%define glib_version 2.6.0
%define gtk_version 2.8.0
%define gstreamer_version 0.10.3
%define gconf_version 2.14
%define gnome_media_version 2.11.91
%define scrollkeeper_version 0.3.5

Name:		sound-juicer
Summary:	Clean and lean CD ripper
Version:	2.28.1
Release:	6%{?dist}
License:	GPLv2+
Group:		Applications/Multimedia
Source:		http://download.gnome.org/sources/sound-juicer/2.28/%{name}-%{version}.tar.bz2
URL:		http://www.burtonini.com/blog/computers/sound-juicer
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
Requires:	cdparanoia

Requires(pre): GConf2 >= %{gconf_version}
Requires(post): GConf2 >= %{gconf_version}
Requires(preun): GConf2 >= %{gconf_version}
Requires(post): scrollkeeper
Requires(postun): scrollkeeper
Requires(post): desktop-file-utils
Requires(postun): desktop-file-utils

BuildRequires:  gnome-media-devel >= %{gnome_media_version}
BuildRequires:	libmusicbrainz3-devel
BuildRequires:	glib2-devel >= %{glib_version}
BuildRequires:	gtk2-devel >= %{gtk_version}
BuildRequires:	gstreamer-devel >= %{gstreamer_version}
BuildRequires:	gstreamer-plugins-base-devel
BuildRequires:	gstreamer-plugins-good-devel
BuildRequires:	gnome-doc-utils
BuildRequires:	GConf2-devel >= %{gconf_version}
BuildRequires:  brasero-devel
BuildRequires:  scrollkeeper >= %{scrollkeeper_version}
BuildRequires:  gcc-c++
BuildRequires:  gettext intltool
BuildRequires:  libcanberra-devel
BuildRequires:  libglade2-devel
BuildRequires:  gnome-common
BuildRequires:  automake autoconf libtool
BuildRequires:  desktop-file-utils

ExcludeArch: s390 s390x

# http://git.gnome.org/browse/sound-juicer/patch/?id=7f94a7b90f823a123bd7aaa2f49600aabfcbc24b
Patch0:		sound-juicer-mb-crasher.patch

# make documentation show up in rarian/yelp
Patch1: sound-juicer-doc-category.patch

# updated translations
# https://bugzilla.redhat.com/show_bug.cgi?id=589179
Patch2: sound-juicer-translations.patch

%description
GStreamer-based CD ripping tool. Saves audio CDs to Ogg/vorbis.

%prep
%setup -q
%patch0 -p1 -b .mb-crasher
%patch1 -p1 -b .doc-category
%patch2 -p1 -b .translations

%build
# work around a gstreamer problem where it
# doesn't find plugins the first time around
DBUS_FATAL_WARNINGS=0 /usr/bin/gst-inspect-0.10 --print-all
%configure --disable-scrollkeeper

# drop unneeded direct library deps with --as-needed
# libtool doesn't make this easy, so we do it the hard way
sed -i -e 's/ -shared / -Wl,-O1,--as-needed\0 /g' -e 's/    if test "$export_dynamic" = yes && test -n "$export_dynamic_flag_spec"; then/      func_append compile_command " -Wl,-O1,--as-needed"\n      func_append finalize_command " -Wl,-O1,--as-needed"\n\0/' libtool
# Remove RPATH
sed -i 's|^hardcode_libdir_flag_spec=.*|hardcode_libdir_flag_spec=""|g' libtool
sed -i 's|^runpath_var=LD_RUN_PATH|runpath_var=DIE_RPATH_DIE|g' libtool

export tagname=CC
make AM_CFLAGS=-export-dynamic


%install
rm -rf $RPM_BUILD_ROOT
export GCONF_DISABLE_MAKEFILE_SCHEMA_INSTALL=1;
make install DESTDIR=$RPM_BUILD_ROOT
unset GCONF_DISABLE_MAKEFILE_SCHEMA_INSTALL

rm -rf $RPM_BUILD_ROOT%{_localstatedir}/scrollkeeper
rm -f $RPM_BUILD_ROOT%{_datadir}/icons/hicolor/icon-theme.cache

desktop-file-install \
	--add-category="X-AudioVideoImport" \
	--dir=%{buildroot}%{_datadir}/applications \
	$RPM_BUILD_ROOT/%{_datadir}/applications/sound-juicer.desktop


%find_lang sound-juicer --with-gnome


%clean
rm -rf $RPM_BUILD_ROOT

%pre
if [ "$1" -gt 1 ]; then
    export GCONF_CONFIG_SOURCE=`gconftool-2 --get-default-source`
    gconftool-2 --makefile-uninstall-rule %{_sysconfdir}/gconf/schemas/sound-juicer.schemas > /dev/null || :
fi

%preun
if [ "$1" -eq 0 ]; then
    export GCONF_CONFIG_SOURCE=`gconftool-2 --get-default-source`
    gconftool-2 --makefile-uninstall-rule %{_sysconfdir}/gconf/schemas/sound-juicer.schemas > /dev/null || :
fi

%post
scrollkeeper-update -q
update-desktop-database -q
export GCONF_CONFIG_SOURCE=`gconftool-2 --get-default-source`
gconftool-2 --makefile-install-rule %{_sysconfdir}/gconf/schemas/sound-juicer.schemas > /dev/null || :
touch --no-create %{_datadir}/icons/hicolor
if [ -x /usr/bin/gtk-update-icon-cache ]; then
  /usr/bin/gtk-update-icon-cache -q %{_datadir}/icons/hicolor;
fi

%postun
scrollkeeper-update -q
update-desktop-database -q
touch --no-create %{_datadir}/icons/hicolor
if [ -x /usr/bin/gtk-update-icon-cache ]; then
  /usr/bin/gtk-update-icon-cache -q %{_datadir}/icons/hicolor;
fi

%files -f sound-juicer.lang
%defattr(-, root, root)
%doc AUTHORS COPYING README NEWS
%{_bindir}/sound-juicer
%{_sysconfdir}/gconf/schemas/sound-juicer.schemas
%{_datadir}/sound-juicer
%{_datadir}/applications/sound-juicer.desktop
%{_datadir}/icons/hicolor/*/apps/sound-juicer.png
%{_datadir}/icons/hicolor/*/apps/sound-juicer.svg
%{_mandir}/man1/*

%changelog
* Fri Jun 25 2010 Bastien Nocera <bnocera@redhat.com> 2.28.1-6
- Add missing Requires for update-desktop-database usage in
  the scriptlets
Resolves: #593054

* Fri May 14 2010 Bastien Nocera <bnocera@redhat.com> 2.28.1-5
- Fix package review bugs

* Wed May  5 2010 Matthias Clasen <mclasen@redhat.com> 2.28.1-4
- Update translations
Resolves: #589179

* Mon May  3 2010 Matthias Clasen <mclasen@redhat.com> 2.28.1-3
- Make docs show up in yelp
Resolves: # 588511

* Wed Jan 06 2010 Bastien Nocera <bnocera@redhat.com> 2.28.1-2
- Fix potential crasher in libmusicbrainz
Related: rhbz#543948

* Wed Nov 25 2009 Bastien Nocera <bnocera@redhat.com> 2.28.1-1
- Update to 2.28.1
- Fix crasher on double-free (#539848)

* Tue Oct 27 2009 Bastien Nocera <bnocera@redhat.com> 2.28.0-4
- Fix crasher when extracting a CD that's not in musicbrainz (#528297)

* Mon Sep 28 2009 Richard Hughes  <rhughes@redhat.com> - 2.28.0-3
- Apply a patch from upstream to inhibit gnome-session, rather than
  gnome-power-manager. This fixes a warning on rawhide when using sound-juicer.

* Fri Sep 25 2009 Bastien Nocera <bnocera@redhat.com> 2.28.0-2
- Remove old libmusicbrainz BR

* Wed Sep 23 2009 Matthias Clasen <mclasen@redhat.com> - 2.28.0-1
- Update to 2.28.0

* Wed Sep 23 2009 Orcan Ogetbil <oget[DOT]fedora[AT]gmail[DOT]com> - 2.26.1-6
- Update desktop file according to F-12 FedoraStudio feature

* Wed Jul 29 2009 Matthias Clasen <mclasen@redhat.com> - 2.26.1-5
- Drop unneeded direct deps

* Sun Jul 26 2009 Matthias Clasen <mclasen@redhat.com> - 2.26.1-4
- Rebuild to shrink GConf schemas

* Thu May 07 2009 Bastien Nocera <bnocera@redhat.com> 2.26.1-3
- Update patch for #498764

* Thu May 07 2009 Bastien Nocera <bnocera@redhat.com> 2.26.1-2
- Fix gvfs metadata getter crasher (#498764)

* Sun Apr 12 2009 Matthias Clasen <mclasen@redhat.com> - 2.26.1-1
- Update to 2.26.1
- See http://download.gnome.org/sources/sound-juicer/2.26/sound-juicer-2.26.1.news

* Tue Mar 17 2009 Matthias Clasen <mclasen@redhat.com> - 2.26.0-1
- Update to 2.26.0

* Mon Mar 09 2009 - Bastien Nocera <bnocera@redhat.com> - 2.25.92-1
- Update to 2.25.92

* Mon Mar 02 2009 - Bastien Nocera <bnocera@redhat.com> - 2.25.3-3
- Remove nautilus-cd-burner dependency

* Wed Feb 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.25.3-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Tue Feb 17 2009 Matthias Clasen <mclasen@redhat.com> - 2.25.3-1
- Update to 2.25.3

* Tue Feb 03 2009 - Bastien Nocera <bnocera@redhat.com> - 2.25.2-1
- Update to 2.25.2
- Use libmusicbrainz3 in addition to the old one, replace ncb dep with brasero
- Remove a lot of GNOME BRs

* Thu Nov 23 2008 Matthias Clasen <mclasen@redhat.com> - 2.25.1-1
- Update to 2.25.1

* Sun Sep 21 2008 Matthias Clasen <mclasen@redhat.com> - 2.24.0-1
- Update to 2.24.0

* Mon Sep 08 2008 - Bastien Nocera <bnocera@redhat.com> - 2.23.3-1
- Update to 2.23.3

* Fri Aug 22 2008 Matthias Clasen <mclasen@redhat.com> - 2.23.2-1
- Update to 2.23.2

* Tue Aug  5 2008 Matthias Clasen <mclasen@redhat.com> - 2.23.1-1
- Update to 2.23.1

* Thu Jul 10 2008 Matthias Clasen <mclasen@redhat.com> - 2.23.0-2
- There is need to BR hal anymore

* Mon Jun 09 2008 - Bastien Nocera <bnocera@redhat.com> - 2.23.0-1
- Update to 2.23.0

* Tue Apr 29 2008 - Bastien Nocera <bnocera@redhat.com> - 2.22.0-3
- Handle URIs from gvfs

* Wed Mar 12 2008 - Bastien Nocera <bnocera@redhat.com> - 2.22.0-2
- Remove the ExcludeArch

* Mon Mar 10 2008 Matthias Clasen <mclasen@redhat.com> - 2.22.0-1
- Update to 2.22.0

* Tue Mar 04 2008 - Bastien Nocera <bnocera@redhat.com> - 2.21.92-2
- ExcludeArch ppc and ppc64 added (#435771)

* Tue Feb 26 2008  Matthias Clasen <mclasen@redhat.com> - 2.21.92-1
- Update to 2.21.92

* Thu Feb 14 2008  Matthias Clasen <mclasen@redhat.com> - 2.21.91-1
- Update to 2.21.91

* Thu Jan 31 2008  Matthias Clasen <mclasen@redhat.com> - 2.21.3-1
- Update to 2.21.3

* Fri Jan 18 2008  Matthias Clasen <mclasen@redhat.com> - 2.21.2-2
- Add content-type support

* Mon Jan 14 2008  Matthias Clasen <mclasen@redhat.com> - 2.21.2-1
- Update to 2.21.2

* Tue Jan 08 2008 - Bastien Nocera <bnocera@redhat.com> - 2.21.1-1
- Update to 2.21.1

* Fri Dec 21 2007 Matthias Clasen <mclasen@redhat.com> - 2.21.0-1
- Update to 2.21.0

* Mon Oct 15 2007 Matthias Clasen <mclasen@redhat.com> - 2.20.1-1
- Update to 2.20.1 (crash fixes)

* Thu Sep 20 2007 - Bastien Nocera <bnocera@redhat.com> - 2.20.0-2
- Fix crasher when editing profiles and the profile gets unref'ed
  (#278861)

* Mon Sep 17 2007 Matthias Clasen <mclasen@redhat.com> - 2.20.0-1
- Update to 2.20.0

* Sat Aug 25 2007 - Bastien Nocera <bnocera@redhat.com> - 2.19.3-3
- Remove work-around for gst-inspect crashing

* Fri Aug 24 2007 Adam Jackson <ajax@redhat.com> - 2.19.3-2
- Rebuild for build ID

* Mon Aug 13 2007 Matthias Clasen <mclasen@redhat.com> - 2.19.3-1
- Update to 2.19.3

* Tue Aug  7 2007 Matthias Clasen <mclasen@redhat.com> - 2.19.2-2
- Update license field
- Use %%find_lang for help files

* Mon Jun 18 2007 Matthias Clasen <mclasen@redhat.com> - 2.19.2-1
- Update to 2.19.2

* Sat May 19 2007 Matthias Clasen <mclasen@redhat.com> - 2.19.1-1
- Update to 2.19.1

* Tue Apr 17 2007 - Bastien Nocera <bnocera@redhat.com> - 2.16.4-1
- Update to 2.16.4 to get xdg-users-dir support, fix #236658, and
  follow the device selection in the control-center

* Tue Feb 20 2007 - Bastien Nocera <bnocera@redhat.com> - 2.16.3-1
- Update to 2.16.3

* Sat Feb  3 2007 Matthias Clasen <mclasen@redhat.com> - 2.16.2-3
- Minor fixes from package review:
 * Remove unnecessary Requires
 * Add URL
 * Correct Source, BuildRoot
 * Fix directory ownership

* Thu Jan 25 2007 Alexander Larsson <alexl@redhat.com> - 2.16.2-2
- Remove hicolor icon theme cache (#223483)

* Tue Dec  5 2006 Matthias Clasen <mclasen@redhat.com> - 2.16.2-1
- Update to 2.16.2

* Sat Oct 22 2006 Matthias Clasen <mclasen@redhat.com> - 2.16.1-1
- Update to 2.16.1

* Wed Oct 18 2006 Matthias Clasen <mclasen@redhat.com> - 2.16.0-2
- Fix scripts according to the packaging guidelines

* Mon Sep  4 2006 Matthias Clasen <mclasen@redhat.com> - 2.16.0-1.fc6
- Update to 2.16.0

* Sun Aug 20 2006 Matthias Clasen <mclasen@redhat.com> - 2.15.5.1-1.fc6
- Update to 2.15.5.1

* Thu Aug  3 2006 Matthias Clasen <mclasen@redhat.com> - 2.15.4-1.fc6
- Update to 2.15.4

* Wed Jul 19 2006 Matthias Clasen <mclasen@redhat.com> - 2.15.3-3
- Rebuild against dbus

* Wed Jul 12 2006 Jesse Keating <jkeating@redhat.com> - 2.15.3-2.1
- rebuild

* Wed Jun 14 2006 Matthias Clasen <mclasen@redhat.com> - 2.15.3-2
- Work around a gstreamer problem

* Wed Jun 14 2006 Matthias Clasen <mclasen@redhat.com> - 2.15.3-1
- Update to 2.15.3

* Sat Jun 10 2006 Matthias Clasen <mclasen@redhat.com> - 2.15.2.1-3
- More missing BuildRequires

* Sat May 20 2006 Matthias Clasen <mclasen@redhat.com> - 2.15.2.1-2
- Add missing BuildRequires (#182174)

* Tue May 17 2006 Matthias Clasen <mclasen@redhat.com> - 2.15.2.1-1
- Update to 2.15.2.1

* Mon Apr 17 2006 Matthias Clasen <mclasen@redhat.com> - 2.14.3-2
- Update to 2.14.3

* Mon Apr 10 2006 Matthias Clasen <mclasen@redhat.com> - 2.14.2-2
- Update to 2.14.2

* Wed Apr  5 2006 Matthias Clasen <mclasen@redhat.com> - 2.14.1-2
- Update to 2.14.1

* Sun Mar 12 2006 Matthias Clasen <mclasen@redhat.com> - 2.14.0-1
- Update to 2.14.0

* Tue Feb 28 2006 Matthias Clasen <mclasen@redhat.com> - 2.13.6-1
- Update to 2.13.6

* Sun Feb 12 2006 Matthias Clasen <mclasen@redhat.com> - 2.13.5-1
- Update to 2.13.5

* Fri Feb 10 2006 Jesse Keating <jkeating@redhat.com> - 2.13.4-3.2
- bump again for double-long bug on ppc(64)

* Tue Feb 07 2006 Jesse Keating <jkeating@redhat.com> - 2.13.4-3.1
- rebuilt for new gcc4.1 snapshot and glibc changes

* Sun Feb  5 2006 Christopher Aillon <caillon@redhat.com> 2.13.4-3
- Fix broken Requires

* Sat Feb  4 2006 Christopher Aillon <caillon@redhat.com> 2.13.4-2
- Update to use gstreamer (0.10)

* Mon Jan 30 2006 Matthias Clasen <mclasen@redhat.com> 2.13.4-1
- Update to 2.13.4

* Mon Jan 09 2006 John (J5) Palmieri <johnp@redhat.com> 2.13.2-1
- Upgrade to 2.13.2

* Mon Jan 09 2006 John (J5) Palmieri <johnp@redhat.com> 2.13.1-4
- Add a patch that adds -Wl,--export-dynamic to the build

* Thu Jan 05 2006 John (J5) Palmieri <johnp@redhat.com> 2.13.1-3
- GStreamer has been split into gstreamer08 and gstreamer (0.10) packages
  we need gstreamer08 for now

* Fri Dec 09 2005 Jesse Keating <jkeating@redhat.com>
- rebuilt

* Fri Dec 02 2005 John (J5) Palmieri <johnp@redhat.com> 2.13.1-2
- Rebuild with new libnautilus-cd-burner

* Wed Aug 17 2005 Matthias Clasen <mclasen@redhat.com> 2.13.1-1
- Update to 2.13.1

* Wed Aug 17 2005 Matthias Clasen <mclasen@redhat.com> 2.11.91-1
- Newer upstream version

* Tue Jul 12 2005 Matthias Clasen <mclasen@redhat.com> 2.11.3-1
- Newer upstream version

* Mon Apr 04 2005 John (J5) Palmieri <johnp@redhat.com> 2.10.1-1
- update to upstream 2.10.1 which should fix crashes when clicking
  extract

* Wed Mar 23 2005 John (J5) Palmieri <johnp@redhat.com> 2.10.0-2
- Rebuild for libmusicbrainz-2.1.1

* Fri Mar 11 2005 John (J5) Palmieri <johnp@redhat.com> 2.10.0-1
- Update to upstream version 2.10.0 

* Tue Mar 08 2005 John (J5) Palmieri <johnp@redhat.com> 2.9.91-3
- Build in rawhide
- Disable build on s390 and s390x

* Fri Feb 25 2005 John (J5) Palmieri <johnp@redhat.com> 2.9.91-2
- Reenabled BuildRequires for hal-devel >= 0.5.0
- Added (Build)Requires for nautilus-cd-burner(-devel) >= 2.9.6

* Wed Feb 23 2005 John (J5) Palmieri <johnp@redhat.com> 2.9.91-1
- New upstream version (version jump resulted from sound-juicer using gnome
  versioning scheme)
  
* Fri Feb 04 2005 Colin Walters <walters@redhat.com> 0.6.0-1
- New upstream version
- Remove obsoleted sound-juicer-idle-safety.patch
- BR latest gnome-media

* Fri Nov 12 2004 Warren Togami <wtogami@redhat.com> 0.5.14-5
- minor spec cleanups
- req cdparanoia and gstreamer-plugins

* Tue Nov 09 2004 Colin Walters <walters@redhat.com> 0.5.14-4
- Add sound-juicer-idle-safety.patch (bug 137847)

* Wed Oct 27 2004 Colin Walters <walters@redhat.com> 0.5.14-2
- Actually enable HAL
- BR hal-devel

* Wed Oct 13 2004 Colin Walters <walters@redhat.com> 0.5.14-1
- New upstream
- This release fixes corruption on re-read, upstream 153085
- Remove upstreamed sound-juicer-0.5.13-prefs-crash.patch

* Mon Oct 04 2004 Colin Walters <walters@redhat.com> 0.5.13-2
- Apply patch to avoid prefs crash

* Tue Sep 28 2004 Colin Walters <walters@redhat.com> 0.5.13-1
- New upstream 0.5.13

* Mon Sep 27 2004 Colin Walters <walters@redhat.com> 0.5.12.cvs20040927-1
- New upstream CVS snapshot, 20040927

* Mon Sep 20 2004 Colin Walters <walters@redhat.com> 0.5.12-1
- New upstream version 0.5.12
- Delete upstreamed patch sound-juicer-0.5.9-pref-help.patch
- Delete upstreamed patch sound-juicer-0.5.10-gstreamer.patch
- Delete call to autoconf

* Tue Jun 15 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Tue Mar 16 2004 Jeremy Katz <katzj@redhat.com> 0.5.10.1-8
- rebuild for new gstreamer

* Thu Mar 11 2004 Brent Fox <bfox@redhat.com> 0.5.10.1-5
- rebuild

* Fri Feb 27 2004 Brent Fox <bfox@redhat.com> 0.5.10.1-3
- rebuild

* Fri Feb 13 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Thu Feb  5 2004 Brent Fox <bfox@redhat.com> 0.5.10.1-1
- new version

* Wed Jan 28 2004 Alexander Larsson <alexl@redhat.com> 0.5.9-4
- rebuild to use new gstreamer

* Fri Jan 16 2004 Brent Fox <bfox@redhat.com> 0.5.9-3
- add preun to clean up GConf entries on uninstall

* Wed Jan 14 2004 Brent Fox <bfox@redhat.com> 0.5.9-2
- create init patch to make help work

* Tue Jan 13 2004 Brent Fox <bfox@redhat.com> 0.5.9-1
- update to 0.5.9

* Mon Dec 15 2003 Christopher Blizzard <blizzard@redhat.com> 0.5.8-1
- Add upstream patch that fixes permissions of created directories.

* Wed Dec 03 2003 Christopher Blizzard <blizzard@redhat.com> 0.5.8-0
- Update to 0.5.8

* Tue Oct 21 2003 Brent Fox <bfox@redhat.com> 0.5.5-1
- update to 0.5.5-1

* Mon Sep  1 2003 Jonathan Blandford <jrb@redhat.com>
- warning dialog fix
- add a quality option

* Fri Aug 29 2003 Elliot Lee <sopwith@redhat.com> 0.5.2-5
- scrollkeeper stuff should be removed

* Wed Aug 27 2003 Brent Fox <bfox@redhat.com> 0.5.2-4
- remove ExcludeArches since libmusicbrainz is building on all arches now

* Wed Aug 27 2003 Brent Fox <bfox@redhat.com> 0.5.2-3
- bump relnum

* Wed Aug 27 2003 Brent Fox <bfox@redhat.com> 0.5.2-2
- spec file cleanups
- add exclude arch for ia64, x86_64, ppc64, and s390x
- add file macros
- remove Requires for gstreamer-cdparanoia and gstreamer-vorbis

* Tue Apr 22 2003 Frederic Crozat <fcrozat@mandrakesoft.com>
- Use more macros

* Sun Apr 20 2003 Ronald Bultje <rbultje@ronald.bitfreak.net>
- Make spec file for sound-juicer (based on netRB spec file)
