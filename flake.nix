{
  description = "A flake for setting up environment for results_show";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-23.05";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = {
    self,
    nixpkgs,
    flake-utils,
  }: let
    systems = with flake-utils.lib.system; [
      x86_64-linux
      aarch64-linux
    ];
  in
    flake-utils.lib.eachSystem systems (system: let
      pkgs = nixpkgs.legacyPackages.${system};
    in {

      # Development shell
      devShell = pkgs.mkShell {
        buildInputs = with pkgs; [
          iperf
          (python3.withPackages (ps:
            with ps; [
              robotframework
              # self.packages.${system}.PyP100
              numpy
              matplotlib
              pyserial
              paramiko
            ]))
        ];
      };

      # Allows formatting files with `nix fmt`
      formatter = pkgs.alejandra;
    });
}
