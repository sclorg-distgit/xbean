%global pkg_name xbean
%{?scl:%scl_package %{pkg_name}}
%{?maven_find_provides_and_requires}

Name:           %{?scl_prefix}%{pkg_name}
Version:        3.13
Release:        6.5%{?dist}
Summary:        Java plugin based web server
License:        ASL 2.0
URL:            http://geronimo.apache.org/xbean/
Source0:        http://repo2.maven.org/maven2/org/apache/%{pkg_name}/%{pkg_name}/%{version}/%{pkg_name}-%{version}-source-release.zip
BuildArch:      noarch

# Patch for XBEAN-255 from upstream revisions 1538850, 1539053 and
# 1539056.  Removes unnecessary doPrivleged() calls which can cause
# problems.
Patch0:         %{pkg_name}-XBEAN-255.patch

BuildRequires:  %{?scl_prefix}maven-local
BuildRequires:  %{?scl_prefix}mvn(asm:asm)
BuildRequires:  %{?scl_prefix}mvn(asm:asm-commons)
BuildRequires:  %{?scl_prefix}mvn(commons-logging:commons-logging-api)
BuildRequires:  %{?scl_prefix}mvn(junit:junit)
BuildRequires:  %{?scl_prefix}mvn(log4j:log4j)
BuildRequires:  %{?scl_prefix}mvn(org.apache.felix:felix-parent)
BuildRequires:  %{?scl_prefix}mvn(org.apache.felix:maven-bundle-plugin)
BuildRequires:  %{?scl_prefix}mvn(org.apache.felix:org.apache.felix.framework)
BuildRequires:  %{?scl_prefix}mvn(org.apache.maven.plugins:maven-source-plugin)
BuildRequires:  %{?scl_prefix}mvn(org.osgi:org.osgi.core)
BuildRequires:  %{?scl_prefix}mvn(org.slf4j:slf4j-api)

%description
The goal of XBean project is to create a plugin based server
analogous to Eclipse being a plugin based IDE. XBean will be able to
discover, download and install server plugins from an Internet based
repository. In addition, we include support for multiple IoC systems,
support for running with no IoC system, JMX without JMX code,
lifecycle and class loader management, and a rock solid Spring
integration.

%package        javadoc
Summary:        API documentation for %{pkg_name}

%description    javadoc
This package provides %{summary}.

%prep
%setup -q -n %{pkg_name}-%{version}
%{?scl:scl enable %{scl} - <<"EOF"}
set -e -x
%patch0

# build failing on this due to doxia-sitetools problems
rm src/site/site.xml

%pom_remove_parent
%pom_remove_dep mx4j:mx4j
%pom_remove_dep :xbean-asm-shaded xbean-reflect

# These aren't needed for now
%pom_disable_module xbean-asm-shaded
%pom_disable_module xbean-finder-shaded
%pom_disable_module xbean-telnet

# Prevent modules depending on springframework from building.
%pom_remove_dep org.springframework:
%pom_disable_module xbean-blueprint
%pom_disable_module xbean-classloader
%pom_disable_module xbean-spring
%pom_disable_module maven-xbean-plugin

# Replace generic OSGi dependencies with Apache Felix
%pom_remove_dep :org.osgi.core xbean-bundleutils
%pom_remove_dep org.eclipse:osgi xbean-bundleutils
%pom_add_dep org.apache.felix:org.apache.felix.framework xbean-bundleutils
rm -rf xbean-bundleutils/src/main/java/org/apache/xbean/osgi/bundle/util/equinox/

# Fix dependency on xbean-asm-shaded to original objectweb-asm
sed -i 's/org.apache.xbean.asm/org.objectweb.asm/' \
    xbean-reflect/src/main/java/org/apache/xbean/recipe/XbeanAsmParameterNameLoader.java

# Fix ant groupId
find -name pom.xml -exec sed -i "s|<groupId>ant</groupId>|<groupId>org.apache.ant</groupId>|" {} \;
# Fix cglib artifactId
find -name pom.xml -exec sed -i "s|<artifactId>cglib-nodep</artifactId>|<artifactId>cglib</artifactId>|" {} \;
%{?scl:EOF}

%build
%{?scl:scl enable %{scl} - <<"EOF"}
set -e -x
%mvn_build -f
%{?scl:EOF}

%install
%{?scl:scl enable %{scl} - <<"EOF"}
set -e -x
%mvn_install
%{?scl:EOF}

%files -f .mfiles
%doc LICENSE NOTICE
%dir %{_javadir}/%{pkg_name}

%files javadoc -f .mfiles-javadoc
%doc LICENSE NOTICE

%changelog
* Mon May 26 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 3.13-6.5
- Mass rebuild 2014-05-26

* Wed Feb 19 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 3.13-6.4
- Mass rebuild 2014-02-19

* Tue Feb 18 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 3.13-6.3
- Mass rebuild 2014-02-18

* Thu Feb 13 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 3.13-6.2
- Rebuild to regenerate auto-requires

* Tue Feb 11 2014 Mikolaj Izdebski <mizdebsk@redhat.com> - 3.13-6.1
- First maven30 software collection build

* Fri Dec 27 2013 Daniel Mach <dmach@redhat.com> - 3.13-6
- Mass rebuild 2013-12-27

* Thu Nov  7 2013 Mikolaj Izdebski <mizdebsk@redhat.com> - 3.13-5
- Add patch for XBEAN-255

* Tue Aug 27 2013 Mikolaj Izdebski <mizdebsk@redhat.com> - 3.13-4
- Expand conditionals
- Migrate away from mvn-rpmbuild

* Fri Jun 28 2013 Mikolaj Izdebski <mizdebsk@redhat.com> - 3.13-3
- Rebuild to regenerate API documentation
- Resolves: CVE-2013-1571

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
