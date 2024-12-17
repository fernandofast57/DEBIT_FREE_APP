
{ pkgs }: {
  deps = [
    pkgs.mailutils
    pkgs.imagemagick_light
    pkgs.solc
    pkgs.python39
    pkgs.nodejs
    pkgs.nodePackages.web3
  ];
}
