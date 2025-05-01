{
  lib,
  stdenv,
  fetchurl,
  unzip,
}:
stdenv.mkDerivation rec {
  pname = "LKH";
  version = "2.0.10";

  src = fetchurl {
    url = "http://webhotel4.ruc.dk/~keld/research/LKH/LKH-${version}.tgz";
    sha256 = "1nl86n8qcx8znbq9rfghx8mgbb36iwanlj5lfjrpdm2hv19zqwjj";
  };

  nativeBuildInputs = [unzip];
  buildPhase = ''
    make
  '';

  installPhase = ''
    mkdir -p $out/bin
    cp LKH $out/bin/
  '';

  meta = with lib; {
    description = "The Traveling Salesman Problem solver LKH";
    homepage = "http://webhotel4.ruc.dk/~keld/research/LKH/";
    license = licenses.mit;
    platforms = platforms.linux;
  };
}
