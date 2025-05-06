- Dependencies:
  All dependencies are listed in the `flake.nix` file. If you use the nix package manager, with flakes enabled, and with `devenv` installed, you can run `nix develop --no-pure-eval`.
  This will create a shell with all dependencies installed. Then, to start the `postgresql` service, run `devenv up`. If you do not have the nix package manager, just download the
  packages that are listed in the flake, and start `postgres` manually. I made a small shell script, `dependencies/create_db.nix` to create the databases and fill with OSM data.
  This data needs to be downloaded from geofabrik, and stored in a directory called `data`.

- How to run:
  First, run `create_db` and all databases get created and filled. Then move into the `project/` directory and run the `main.py` file.
