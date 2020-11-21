{
  description = "A modern and flexible dynamic DNS client";

  inputs = {
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils, }:
    with flake-utils.lib;
    eachSystem allSystems (system: let
      pkgs = nixpkgs.legacyPackages.${system};
    in {
      defaultPackage = pkgs.python3Packages.callPackage ./. { };

      defaultApp = {
        type = "app";
        program = "${self.defaultPackage.${system}}/bin/dnsupdate";
      };

      devShell = self.defaultPackage.${system};
    }) //
    eachSystem [ "x86_64-linux" ] (system: {
      hydraJobs.build = self.defaultPackage.${system};
    });
}
