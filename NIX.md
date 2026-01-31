# Nix

## Installation

There is a community maintained Nix flake available in this repository. This flake can be used to run or install the program on NixOS or other distributions.

Run the program once without installing:

```bash
nix run --no-write-lock-file github:JordanL2/ModularCalculatorInterface
```

Install the program:

```bash
nix profile add --no-write-lock-file github:JordanL2/ModularCalculatorInterface
```

Add to system configuration (NixOS only):

```nix
# In flake.nix
{
  inputs = {
    modularcalculator.url = "github:JordanL2/ModularCalculatorInterface";
  };

  outputs = { modularcalculator, ... }: {
    nixosConfigurations.<host> = nixpkgs.lib.nixosSystem {
      modules = [
        ./configuration.nix
      ];
      specialArgs = {
        inherit modularcalculator;
      };
    };
  };
}

# in configuration.nix
{ modularcalculator, ... }:
{
    environment.systemPackages = [
        modularcalculator.packages.x86_64-linux.default
    ];
}
```

Install python library (NixOS only):

```nix
# in configuration.nix
{ pkgs, modularcalculator, ... }:
{
    environment.systemPackages = [
        (pkgs.python3.withPackages([
            modularcalculator.packages.x86_64-linux.python
        ]))
    ];
}
```

## Uninstallation

```bash
nix profile remove ModularCalculatorInterface
```