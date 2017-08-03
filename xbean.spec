%{?scl:%scl_package xbean}
%{!?scl:%global pkg_name %{name}}

# Conditionals to help breaking eclipse <-> xbean dependency cycle
# when bootstrapping for new architectures
%bcond_without equinox
%bcond_without groovy
%bcond_without spring

Name:           %{?scl_prefix}xbean
Version:        4.5
Release:        7.1%{?dist}
Summary:        Java plugin based web server
License:        ASL 2.0
URL:            http://geronimo.apache.org/xbean/
BuildArch:      noarch

Source0:        http://repo2.maven.org/maven2/org/apache/%{pkg_name}/%{pkg_name}/%{version}/%{pkg_name}-%{version}-source-release.zip

# Fix dependency on xbean-asm4-shaded to original objectweb-asm
Patch0:         0001-Unshade-ASM.patch
# Compatibility with Eclipse Luna (rhbz#1087461)
Patch1:         0002-Port-to-Eclipse-Luna-OSGi.patch
Patch2:         0003-Port-to-QDox-2.0.patch

BuildRequires:  %{?scl_prefix}maven-local
BuildRequires:  %{?scl_prefix}mvn(commons-logging:commons-logging-api)
BuildRequires:  %{?scl_prefix}mvn(log4j:log4j:1.2.12)
BuildRequires:  %{?scl_prefix}mvn(org.apache.felix:maven-bundle-plugin)
BuildRequires:  %{?scl_prefix}mvn(org.apache.maven.plugins:maven-source-plugin)
BuildRequires:  %{?scl_prefix}mvn(org.osgi:org.osgi.core)
BuildRequires:  %{?scl_prefix}mvn(org.ow2.asm:asm)
BuildRequires:  %{?scl_prefix}mvn(org.ow2.asm:asm-commons)
BuildRequires:  %{?scl_prefix}mvn(org.slf4j:slf4j-api)

%if %{with equinox}
BuildRequires:  mvn(org.eclipse:osgi)
%endif

%if %{with groovy}
BuildRequires:  mvn(org.codehaus.groovy:groovy-all)
%endif

%if %{with spring}
BuildRequires:  %{?scl_prefix}mvn(ant:ant)
BuildRequires:  %{?scl_prefix}mvn(commons-logging:commons-logging)
BuildRequires:  %{?scl_prefix}mvn(com.thoughtworks.qdox:qdox)
BuildRequires:  %{?scl_prefix}mvn(org.apache.maven:maven-archiver)
BuildRequires:  %{?scl_prefix}mvn(org.apache.maven:maven-artifact)
BuildRequires:  %{?scl_prefix}mvn(org.apache.maven:maven-plugin-api)
BuildRequires:  %{?scl_prefix}mvn(org.apache.maven:maven-project)
BuildRequires:  %{?scl_prefix}mvn(org.apache.maven.plugins:maven-antrun-plugin)
BuildRequires:  %{?scl_prefix}mvn(org.apache.maven.plugins:maven-plugin-plugin)
BuildRequires:  %{?scl_prefix}mvn(org.codehaus.plexus:plexus-archiver)
BuildRequires:  %{?scl_prefix}mvn(org.codehaus.plexus:plexus-utils)
BuildRequires:  mvn(org.springframework:spring-beans)
BuildRequires:  mvn(org.springframework:spring-context)
BuildRequires:  mvn(org.springframework:spring-web)
%endif

%description
The goal of XBean project is to create a plugin based server
analogous to Eclipse being a plugin based IDE. XBean will be able to
discover, download and install server plugins from an Internet based
repository. In addition, we include support for multiple IoC systems,
support for running with no IoC system, JMX without JMX code,
lifecycle and class loader management, and a rock solid Spring
integration.

%if %{with spring}
# For now blueprint module fails to compile. Disable it.
%if 0

%package        blueprint
Summary:        Schema-driven namespace handler for Apache Aries Blueprint

%description    blueprint
This package provides %{summary}.
%endif

%package        classloader
Summary:        A flexibie multi-parent classloader

%description    classloader
This package provides %{summary}.

%package        spring
Summary:        Schema-driven namespace handler for spring contexts
Requires:       %{name} = %{version}-%{release}

%description    spring
This package provides %{summary}.

%package        -n %{?scl_prefix}maven-%{pkg_name}-plugin
Summary:        XBean plugin for Apache Maven

%description    -n %{?scl_prefix}maven-%{pkg_name}-plugin
This package provides %{summary}.
%endif

%package        javadoc
Summary:        API documentation for %{pkg_name}

%description    javadoc
This package provides %{summary}.

%prep
%setup -n %{pkg_name}-%{version} -q
# build failing on this due to doxia-sitetools problems
rm src/site/site.xml

%patch0 -p1
%if %{with equinox}
%patch1 -p1
%endif
%patch2 -p1

%pom_remove_parent
%pom_remove_dep mx4j:mx4j

%pom_remove_dep -r :xbean-asm5-shaded
%pom_remove_dep -r :xbean-finder-shaded
%pom_disable_module xbean-asm5-shaded
%pom_disable_module xbean-finder-shaded

%pom_xpath_remove pom:scope xbean-asm-util
%pom_xpath_remove pom:optional xbean-asm-util

# Prevent modules depending on springframework from building.
%if %{without spring}
   %pom_remove_dep org.springframework:
   #%%pom_disable_module xbean-blueprint
   %pom_disable_module xbean-classloader
   %pom_disable_module xbean-spring
   %pom_disable_module maven-xbean-plugin
%else
   %mvn_package :xbean-classloader classloader
   %mvn_package :xbean-spring spring
   %mvn_package :maven-xbean-plugin maven-xbean-plugin
%endif
# blueprint FTBFS, disable for now
%pom_disable_module xbean-blueprint

%if %{without equinox}
  %pom_remove_dep :xbean-bundleutils xbean-finder
  rm -r xbean-finder/src/main/java/org/apache/xbean/finder{,/archive}/Bundle*
  %pom_disable_module xbean-bundleutils
%endif

%if %{without groovy}
%pom_disable_module xbean-telnet
%endif

# maven-xbean-plugin invocation makes no sense as there are no namespaces
%pom_remove_plugin :maven-xbean-plugin xbean-classloader

# As auditing tool RAT is useful for upstream only.
%pom_remove_plugin :apache-rat-plugin

# disable copy of internal aries-blueprint
sed -i "s|<Private-Package>|<!--Private-Package>|" xbean-blueprint/pom.xml
sed -i "s|</Private-Package>|</Private-Package-->|" xbean-blueprint/pom.xml

%build
%mvn_build -f

%install
%mvn_install

%files -f .mfiles
%doc LICENSE NOTICE
%dir %{_javadir}/%{pkg_name}

%if %{with spring}
%if 0

%files blueprint -f .mfiles-blueprint
%doc LICENSE NOTICE %{pkg_name}-blueprint/target/restaurant.xsd*
%endif

%files classloader -f .mfiles-classloader
%doc LICENSE NOTICE

%files spring -f .mfiles-spring
%doc LICENSE NOTICE

%files -n %{?scl_prefix}maven-%{pkg_name}-plugin -f .mfiles-maven-%{pkg_name}-plugin
%doc LICENSE NOTICE
%endif

%files javadoc -f .mfiles-javadoc
%doc LICENSE NOTICE

%changelog
* Wed Jun 21 2017 Java Maintainers <java-maint@redhat.com> - 4.5-7.1
- Automated package import and SCL-ization

* Sat Feb 11 2017 Fedora Release Engineering <releng@fedoraproject.org> - 4.5-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Wed Feb  1 2017 Mikolaj Izdebski <mizdebsk@redhat.com> - 4.5-6
- Introduce groovy build conditional

* Wed Feb 01 2017 Michael Simacek <msimacek@redhat.com> - 4.5-5
- Fix build with conditionals

* Wed Feb 01 2017 Michael Simacek <msimacek@redhat.com> - 4.5-4
- Port to current QDox

* Thu Jun 16 2016 Mikolaj Izdebski <mizdebsk@redhat.com> - 4.5-3
- Add missing build-requires

* Thu May 12 2016 Michael Simacek <msimacek@redhat.com> - 4.5-2
- Enable xbean-asm-util

* Mon May 02 2016 Michael Simacek <msimacek@redhat.com> - 4.5-1
- Update to upstream version 4.5

* Fri Feb 05 2016 Fedora Release Engineering <releng@fedoraproject.org> - 4.4-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Tue Nov 24 2015 Michael Simacek <msimacek@redhat.com> - 4.4-1
- Update to upstream version 4.4
- Rebase patches
- Remove obsolete groovy patch

* Mon Jul 13 2015 Mikolaj Izdebski <mizdebsk@redhat.com> - 4.3-1
- Update to upstream version 4.3

* Fri Jun 19 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 4.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Wed Apr  1 2015 Mikolaj Izdebski <mizdebsk@redhat.com> - 4.2-1
- Update to upstream version 4.2

* Thu Feb  5 2015 Mikolaj Izdebski <mizdebsk@redhat.com> - 4.1-2
- Fix patch unshading ASM

* Fri Nov 21 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 4.1-1
- Update to upstream version 4.1

* Sun Jun 08 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.17-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Mon Apr 14 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 3.17-1
- Update to upstream version 3.17
- Add patch for Eclipse Luna

* Thu Dec  5 2013 Mikolaj Izdebski <mizdebsk@redhat.com> - 3.16-1
- Update to upstream version 3.16

* Thu Aug 08 2013 Stanislav Ochotnicky <sochotnicky@redhat.com> - 3.13-4
- Update to latest packaging guidelines

* Sun Aug 04 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.13-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Mon Apr 29 2013 Mikolaj Izdebski <mizdebsk@redhat.com> - 3.13-2
- Remove unneeded BR: maven-idea-plugin

* Fri Mar 15 2013 Michal Srb <msrb@redhat.com> - 3.13-1
- Update to upstream version 3.13

* Fri Feb 15 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.12-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Wed Feb 06 2013 Java SIG <java-devel@lists.fedoraproject.org> - 3.12-5
- Update for https://fedoraproject.org/wiki/Fedora_19_Maven_Rebuild
- Replace maven BuildRequires with maven-local

* Mon Dec 17 2012 Mikolaj Izdebski <mizdebsk@redhat.com> - 3.12-4
- Enable xbean-spring, resolves rhbz#887496
- Disable xbean-blueprint due to FTBFS

* Mon Oct 22 2012 Mikolaj Izdebski <mizdebsk@redhat.com> - 3.12-3
- Replace eclipse-rcp requires with eclipse-equinox-osgi
- Reenable Equinox

* Tue Oct 16 2012 gil cattaneo <puntogil@libero.it> - 3.12-2
- Enable xbean-blueprint and xbean-classloader modules

* Wed Oct 10 2012 Mikolaj Izdebski <mizdebsk@redhat.com> - 3.12-1
- Update to upstream version 3.12

* Wed Oct 10 2012 Krzysztof Daniel <kdaniel@redhat.com> 3.11.1-8
- Revert previous changes.

* Wed Oct 10 2012 Krzysztof Daniel <kdaniel@redhat.com> 3.11.1-7
- Disable parts dependent on Eclipse (for bootstraping purpose).

* Wed Oct 10 2012 Mikolaj Izdebski <mizdebsk@redhat.com> - 3.11.1-6
- Implement equinox and spring conditionals

* Mon Sep  3 2012 Mikolaj Izdebski <mizdebsk@redhat.com> - 3.11.1-5
- Fix eclipse requires

* Mon Aug 27 2012 Mikolaj Izdebski <mizdebsk@redhat.com> - 3.11.1-4
- Fix felix-framework enabling patch

* Mon Aug  6 2012 Mikolaj Izdebski <mizdebsk@redhat.com> - 3.11.1-3
- Enable xbean-spring
- Enable maven-xbean-plugin
- Remove RPM bug workaround

* Sun Jul 22 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.11.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Fri Jul 13 2012 Mikolaj Izdebski <mizdebsk@redhat.com> - 3.11.1-1
- Update to the upstream version 3.11.1
- Force use of Equinox instead of Felix
- Convert patch to POM macros

* Thu May  3 2012 Stanislav Ochotnicky <sochotnicky@redhat.com> - 3.8-5
- Remove mx4j from deps (javax.management provided by JDK 1.5+)

* Tue Apr 24 2012 Alexander Kurtakov <akurtako@redhat.com> 3.8-4
- BR felix-framework instead of felix-osgi-core.

* Tue Apr 24 2012 Alexander Kurtakov <akurtako@redhat.com> 3.8-3
- Do not build equinox specific parts for RHEL.

* Sat Jan 14 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.8-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Tue Dec  6 2011 Stanislav Ochotnicky <sochotnicky@redhat.com> - 3.8-1
- Update to latest upstream version
- Build with maven 3
- Packaging & guidelines fixes

* Sat May 28 2011 Marek Goldmann <mgoldman@redhat.com> - 3.7-7
- Added xbean-finder and xbean-bundleutils submodules

* Fri Mar  4 2011 Stanislav Ochotnicky <sochotnicky@redhat.com> - 3.7-6
- Add comment for removing javadoc
- Fix maven 3 build

* Mon Feb 07 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 3.7-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Mon Dec  6 2010 Stanislav Ochotnicky <sochotnicky@redhat.com> - 3.7-4
- Fix pom filename (Resolves rhbz#655827)
- Add depmap for main pom file
- Fixes according to new guidelines (versionless jars, javadocs)

* Fri Jul 30 2010 Stanislav Ochotnicky <sochotnicky@redhat.com> - 3.7-3
- Use javadoc:aggregate to generate javadocs

* Fri Jul  9 2010 Stanislav Ochotnicky <sochotnicky@redhat.com> - 3.7-2
- Add license to javadoc subpackage

* Mon Jun 21 2010 Stanislav Ochotnicky <sochotnicky@redhat.com> - 3.7-1
- First release
