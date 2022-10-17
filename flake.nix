{
  description = "A very basic flake";

    
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-22.05";
    flakeutils.url = "github:numtide/flake-utils";
  };


  outputs = { self, nixpkgs, flakeutils}: 
    flakeutils.lib.eachDefaultSystem (system:
        let pkgs = nixpkgs.legacyPackages.${system}; 
        
        in
        rec {
            devShells.default =  pkgs.mkShell {
                  buildInputs = [
                    (pkgs.python3.withPackages (p: [
                        p.numpy 
                        p.matplotlib 
                        p.setuptools
                        p.scipy 
                        p.tqdm
                        packages.default
                    ]))
                    pkgs.pyright
                  ];
            };

            packages.default = pkgs.python310Packages.callPackage ./pack.nix {}; 


        }
    );

    buildPythonPackage = (python: python.pkgs.callPackage ./pack.nix {}); 
}
