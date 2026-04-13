{
  description = "Home Manager flake: deploy .zshrc from this repository";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    home-manager = {
      url = "github:nix-community/home-manager";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs =
    { self, nixpkgs, home-manager, ... }:
    let
      inherit (nixpkgs) lib;
      linuxSystems = [ "x86_64-linux" "aarch64-linux" ];
      forLinux = f: lib.genAttrs linuxSystems (system: f nixpkgs.legacyPackages.${system});

      mkDeveloper =
        system:
        home-manager.lib.homeManagerConfiguration {
          pkgs = nixpkgs.legacyPackages.${system};
          modules = [
            ./home.nix
            {
              home = {
                username = "developer";
                homeDirectory = "/home/developer";
              };
            }
          ];
        };
    in
    {
      homeConfigurations = {
        developer-x86_64-linux = mkDeveloper "x86_64-linux";
        developer-aarch64-linux = mkDeveloper "aarch64-linux";
      };

      packages = forLinux (pkgs: {
        default = self.homeConfigurations."developer-${pkgs.system}".activationPackage;
      });

      devShells = forLinux (pkgs: {
        default = pkgs.mkShell {
          packages = [ home-manager.packages.${pkgs.system}.default ];
          shellHook = ''
            echo "Apply: home-manager switch --flake path:.#developer-${pkgs.system}"
          '';
        };
      });
    };
}
