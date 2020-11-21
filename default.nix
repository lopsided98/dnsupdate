{ lib, fetchFromGitHub, buildPythonApplication, requests, pyyaml
, networkInterfaceSupport ? true, netifaces ? null
, webScrapingSupport ? true, beautifulsoup4 ? null }:

assert networkInterfaceSupport -> netifaces != null;
assert webScrapingSupport -> beautifulsoup4 != null;

buildPythonApplication {
  pname = "dnsupdate";
  version = "0.3";

  src = ./.;

  propagatedBuildInputs = [ requests pyyaml ]
    ++ lib.optional webScrapingSupport beautifulsoup4
    ++ lib.optional networkInterfaceSupport netifaces;

  meta = with lib; {
    description = "A modern and flexible dynamic DNS client";
    homepage = "https://github.com/lopsided98/dnsupdate";
    license = licenses.gpl3;
    maintainers = with maintainers; [ lopsided98 ];
    platforms = platforms.all;
  };
}
