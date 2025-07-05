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
      packages.default = pkgs.python3Packages.callPackage ./. { };

      devShells.default = self.packages.${system}.default;
    }) //
    eachSystem [ "x86_64-linux" ] (system: {
      hydraJobs.build = self.packages.${system}.default;
    });
}
