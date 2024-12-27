
{ pkgs }: {
  deps = [
    pkgs.python3
    pkgs.python3Packages.pip
    pkgs.python3Packages.flask
    pkgs.python3Packages.sqlalchemy
    pkgs.python3Packages.flask_sqlalchemy
    pkgs.python3Packages.flask_login
    pkgs.python3Packages.flask_migrate
    pkgs.python3Packages.bcrypt
    pkgs.python3Packages.marshmallow
    pkgs.nodejs-16_x
    pkgs.openssl
    pkgs.postgresql
    pkgs.redis
  ];
}
