
{ pkgs }: {
  deps = [
    pkgs.nano
    pkgs.mailutils
    pkgs.imagemagick_light
    pkgs.solc
    pkgs.python3
    pkgs.python3Packages.pip
  ];
}
