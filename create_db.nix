{pkgs, ...}:
pkgs.writeShellScriptBin "create_db" ''
  for file in data/*.osm.pbf; do
  	base=$(basename "$file" -latest.osm.pbf)
  	dbname=$(echo "$base" | sed 's/-/_/g')

  	echo "Creating database: $dbname"
  	psql -c "DROP DATABASE IF EXISTS $dbname;"
  	psql -c "CREATE DATABASE $dbname;"
  	psql -d "$dbname" -c "CREATE EXTENSION postgis;"
  	psql -d "$dbname" -c "CREATE EXTENSION hstore;"
  	osm2pgsql --create --hstore --slim --multi-geometry --database "$dbname" "$file"
  done
''
