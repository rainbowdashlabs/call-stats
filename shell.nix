{ pkgs ? import <nixpkgs> {}, ... }:

let
in
pkgs.mkShell
{
  packages = with pkgs; [nodejs_24 python314];
}

