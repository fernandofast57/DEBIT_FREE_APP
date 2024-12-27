
{ pkgs }: {
  deps = [
    pkgs.python311
    pkgs.python311Packages.pip
    pkgs.python311Packages.flask
    pkgs.python311Packages.sqlalchemy
    pkgs.nodejs-18_x
    pkgs.openssl
    pkgs.postgresql
    pkgs.redis
  ];
}
