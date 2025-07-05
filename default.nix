{
  lib,
  fetchFromGitHub,
  buildPythonApplication,
  setuptools,
  requests,
  pyyaml,
  netifaces,
  beautifulsoup4,
  black,
  flake8,
}:

buildPythonApplication {
  pname = "dnsupdate";
  version = "0.4.1";
  pyproject = true;

  src = ./.;

  nativeBuildInputs = [ setuptools ];

  propagatedBuildInputs = [
    requests
    pyyaml
    netifaces
    beautifulsoup4
  ];

  checkInputs = [
    black
    flake8
  ];

  preCheck = ''
    black --check .
    flake8
  '';

  meta = with lib; {
    description = "A modern and flexible dynamic DNS client";
    homepage = "https://github.com/lopsided98/dnsupdate";
    license = licenses.gpl3;
    maintainers = with maintainers; [ lopsided98 ];
    platforms = platforms.all;
    mainProgram = "dnsupdate";
  };
}
