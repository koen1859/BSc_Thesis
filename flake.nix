{
  description = "A very basic flake";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs?ref=nixos-unstable";
    devenv = {
      url = "github:cachix/devenv";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  nixConfig = {
    extra-trusted-public-keys = "devenv.cachix.org-1:w1cLUi8dv3hnoSPGAuibQv+f9TZLr6cv/Hm9XgU50cw=";
    extra-substituters = "https://devenv.cachix.org";
  };

  outputs = {
    self,
    nixpkgs,
    devenv,
  } @ inputs: let
    system = "x86_64-linux";
    pkgs = nixpkgs.legacyPackages.${system};
  in {
    devenv-up = self.devShells.${system}.default.config.procfileScript;
    devenv-test = self.devShells.${system}.default.config.test;

    devShells.${system}.default = devenv.lib.mkShell {
      inherit inputs pkgs;

      modules = [
        ({pkgs, ...}: {
          packages = [
            (pkgs.python3.withPackages (ps:
              with ps; [
                psycopg
                igraph
                numpy
                matplotlib
                folium
                ujson
                geopandas
                scikit-learn
                pandas
              ]))
            pkgs.osm2pgsql
            (pkgs.callPackage ./dependencies/lkh.nix {})
            (import ./dependencies/create_db.nix {inherit pkgs;})
          ];
          services.postgres = {
            enable = true;
            package = pkgs.postgresql_17;
            extensions = extensions: with extensions; [postgis];
          };
        })
      ];
    };
  };
}
