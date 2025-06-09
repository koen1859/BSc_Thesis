{
  description = "Flake to build the shell for this project";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs?ref=nixos-unstable"; # Where to get the packages from

    # Devenv is a nice way to be able to start services in a development shell
    devenv = {
      url = "github:cachix/devenv";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  # Devenv needs cache, and this makes entering the shell more quick
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
    devenv-up = self.devShells.${system}.default.config.procfileScript; # Command to start services
    devenv-test = self.devShells.${system}.default.config.test;

    # Create the shell
    devShells.${system}.default = devenv.lib.mkShell {
      inherit inputs pkgs;

      modules = [
        (
          {pkgs, ...}: {
            packages = [
              # The python environment
              (
                pkgs.python313.withPackages
                (ps:
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
                    tqdm
                    ipython
                  ])
              )
              (
                pkgs.texliveFull.withPackages
                (ps:
                  with ps; [
                    latexmk
                    amsmath
                    marvosym
                    bbm-macros
                    minted
                    texcount
                    tocbibind
                    latexindent
                    adjustbox
                    algpseudocodex
                    algorithmicx
                    algorithms
                    fifo-stack
                    varwidth
                    tabto-ltx
                    totcount
                  ])
              )
              pkgs.osm2pgsql

              # The LKH package
              (pkgs.callPackage ./dependencies/lkh.nix {})

              # Small script i wrote to fill DBs
              (import ./dependencies/create_db.nix {inherit pkgs;})
            ];

            # We need postgres to store the OSM data
            services.postgres = {
              enable = true;
              package = pkgs.postgresql_17;
              extensions = extensions: with extensions; [postgis];
            };
          }
        )
      ];
    };
  };
}
