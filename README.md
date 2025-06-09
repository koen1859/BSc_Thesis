# Assessment of an approximation method for TSP path length on road networks
- Dependencies:
  All dependencies are listed in the `flake.nix` file. If you use the nix package manager, with flakes enabled you can run `nix develop --no-pure-eval`.
  This will create a shell with all dependencies installed. Then, to start the `postgresql` service, run `devenv up --detached` (to start in the background). If you do not have the nix package manager, just download the
  packages that are listed in the flake, and start `postgres` manually. I made a small shell script, `dependencies/create_db.nix` to create the databases and fill with OSM data.
  This data needs to be downloaded from Geofabrik, and stored in a directory called `data`.

- How to run:
  First, run `create_db` and all databases get created and filled. This is a script created with `nix`, if you do not have `nix` just copy the `dependencies/create_db.nix` contents to a normal shell script and it will work as well. 
Then move into the `project/` directory and run the `main.py` file.
