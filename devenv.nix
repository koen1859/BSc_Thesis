{pkgs, ...}: {
  packages = with pkgs; [
    (python3.withPackages (ps:
      with ps; [
        igraph
        psycopg2
        shapely
        numpy
        matplotlib
        folium
        ujson
        geopandas
        scikit-learn
        pandas
      ]))
    postgresql_17
    postgresql17Packages.postgis
    osm2pgsql
    (pkgs.callPackage ./lkh.nix {})
    (import ./create_db.nix {inherit pkgs;})
  ];

  services.postgres = {
    enable = true;
    package = pkgs.postgresql_17;
    extensions = extensions:
      with extensions; [
        postgis
      ];
  };
}
