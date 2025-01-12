
{ pkgs }: {
  deps = [
    pkgs.sqlite-interactive
    pkgs.nano
    pkgs.mailutils
    pkgs.zip
    pkgs.rsync
    pkgs.python3
    pkgs.python3Packages.pip
    pkgs.python3Packages.flask
    pkgs.python3Packages.sqlalchemy
    pkgs.python3Packages.marshmallow
    pkgs.python3Packages.pytest
    pkgs.python3Packages.pytest-asyncio
    pkgs.python3Packages.pytest-mock
    pkgs.python3Packages.pytest-cov
    pkgs.nodejs_18
    pkgs.openssl
    pkgs.postgresql
    pkgs.redis
    pkgs.lsof
    pkgs.pkg-config
    pkgs.python3Packages.psutil
  ];
}
