{pkgs ? import <nixpkgs> {} }:
with pkgs;
let 
   mpkg = import ./python_shell.nix;
in 
mkShell {
    buildInputs = [(python310Packages.callPackage mpkg {})];
}
