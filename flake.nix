{
  description = "A module to install modular calculator interface.";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-25.11";  # Keep this updated to latest stable
  };

  outputs = { self, nixpkgs, ... }:
  let
    pkgs = import nixpkgs {
      system = "x86_64-linux";
    };
    lib = pkgs.lib;
    modularcalculator = pkgs.python3Packages.buildPythonPackage rec {
        pname = "modularcalculator";
        version = "1.5.0";  # Update this when a new version is released
        pyproject = true;

        src = pkgs.fetchFromGitHub {
            owner = "JordanL2";
            repo = "ModularCalculator";
            tag = version;
            sha256 = "1zzik9mz87637m54hb8x0nxs7fhiij4q9d8bvvr8l74cc1ankf3j";
            # Use the following command to get the sha256 hash when updating:
            # nix-prefetch-url --unpack https://github.com/JordanL2/ModularCalculator/archive/refs/tags/<version>.tar.gz
        };
        
        nativeBuildInputs = with pkgs.python3Packages; [
            setuptools
        ];
        
        dependencies = with pkgs.python3Packages; [
            pyyaml
            scipy
            strct
        ];
        
        postPatch = ''
            sed -i 's/unittest.main(exit=False)/unittest.main(exit=True)/g' tests/testrunner.py
        '';
        
        #checkPhase = ''
        #  PYTHONPATH=$PYTHONPATH:$PWD ${pkgs.python3.interpreter} tests/tests.py
        #'';
        
        meta = {
            description = "Powerful modular calculator engine";
            homepage = "https://github.com/JordanL2/ModularCalculator";
            license = lib.licenses.asl20;
            maintainers = with lib.maintainers; [ Tommimon ];
        };
    };
  in
  {
    packages.x86_64-linux = {
        python = modularcalculator;
        default = pkgs.python3Packages.buildPythonApplication rec {
            pname = "modularcalculator-qt";
            version = "1.5.7";  # Update this when a new version is released
            pyproject = true;

            src = ./.;

            buildInputs = [ pkgs.qt6.qtwayland ];

            nativeBuildInputs = with pkgs; [
                copyDesktopItems
                modularcalculator
                python3Packages.hatchling
                python3Packages.hatch-vcs
                python3Packages.pyyaml
                python3Packages.scipy
                qt6.wrapQtAppsHook
            ];

            propagatedBuildInputs = with pkgs.python3Packages; [
                darkdetect
                modularcalculator
                pillow
                platformdirs
                pyqrcode
                pyqt6
                python-barcode
                pyusb
                pyyaml
                rich
                scipy
                typer
            ];

            desktopItems = [
                (pkgs.makeDesktopItem {
                name = "Modular Calculator";
                exec = "modularcalculator";
                desktopName = "Modular Calculator";
                icon = "modularcalculator-qt";
                })
            ];

            postInstall = ''
                cp -r $src/config $out/config
                for size in 16 24 48 64 128 256; do
                install -Dm644 $src/icons/''${size}x''${size}.png $out/share/icons/hicolor/''${size}x''${size}/apps/modularcalculator-qt.png || true
                done
            '';

            meta = {
                description = "A powerful, scriptable, modular calculator aimed at scientific, engineering or computing work.";
                homepage = "https://github.com/JordanL2/ModularCalculatorInterface";
                license = lib.licenses.asl20;
                maintainers = with lib.maintainers; [ Tommimon ];
                mainProgram = "modularcalculator";
            };
        };
    };
  };
}
