
{ pkgs }: {
  deps = [
    pkgs.python39
    pkgs.python39Packages.flask
    pkgs.python39Packages.flask_sqlalchemy
    pkgs.python39Packages.sqlalchemy
    pkgs.python39Packages.werkzeug
    pkgs.python39Packages.pip
    pkgs.python39Packages.setuptools
    pkgs.nodejs-16_x
    pkgs.openssl
    pkgs.postgresql
    pkgs.redis
  ];
}
