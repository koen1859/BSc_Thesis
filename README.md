I use `devenv` to manage the dependencies for the project, and make a shell. Using `direnv` we 
can make this shell activate automatically when entering this directory. Then, to start the `postgres`
service run `devenv up -d`.
You need to create a directory called `data`, and store the .osm.pbf files from Groningen and
Noord-Holland in there. These files can be downloaded from here: 
https://download.geofabrik.de/europe/netherlands.html. First, run `create_db` to create the databases.
Then, move into the `project` directory and run `python main.py` and the entire project will run.
