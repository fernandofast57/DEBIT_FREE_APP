{ pkgs }: {
  deps = [
    pkgs.python3
    pkgs.python3Packages.pip
    pkgs.python3Packages.flask
    pkgs.python3Packages.sqlalchemy
    pkgs.python3Packages.marshmallow
    pkgs.nodejs_18
    pkgs.openssl
    pkgs.postgresql
    pkgs.redis
  ];
}
