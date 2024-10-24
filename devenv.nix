{ pkgs, lib, config, inputs, ... }:

{
  name = "dmv";
  # https://devenv.sh/basics/
  env = { GREET = "🛠️ Let's hack "; };

  # https://devenv.sh/scripts/
  scripts.hello.exec = "echo $GREET";
  scripts.cat.exec = ''
    bat "$@";
  '';

  # This script is temporary due to two problems:
  #  1. `cz` requires a personal github token to publish a release https://commitizen-tools.github.io/commitizen/tutorials/github_actions/
  #  2. `cz bump` fails to sign in a terminal: https://github.com/commitizen-tools/commitizen/issues/1184
  scripts.release = {
    exec = ''
      rm CHANGELOG.md
      cz bump --files-only --check-consistency
      git tag $(python -c "from src.dmv import __version__; print(__version__)")
    '';
    description = ''
      Release a new version and update the CHANGELOG.
    '';
  };

  # https://devenv.sh/packages/
  packages = with pkgs; [ nixfmt-rfc-style bat jq tealdeer git ];

  languages = {
    # pyright requires npm
    javascript = {
      enable = true;
      package = pkgs.nodejs_21;
      npm = {
        enable = true;
        package = pkgs.nodejs_21;
        install.enable = true;
      };
    };

    python = {
      enable = true;
      venv = {
        enable = true;
        requirements = ''
          pdm
          python-lsp-server
          importmagic
          epc
          black
        '';
      };
    };
  };

  # Java is required for PySpark
  languages.java.enable = true;
  languages.java.jdk.package = pkgs.jdk8; # Java version running on AWS Glue

  enterShell = ''
    hello
    pdm install
  '';

  # https://devenv.sh/pre-commit-hooks/
  pre-commit.hooks = {
    nixfmt = {
      enable = true;
      package = pkgs.nixfmt-rfc-style;
      excludes = [ ".devenv.flake.nix" ];
    };
    yamllint = {
      enable = true;
      settings.preset = "relaxed";
      settings.configuration = ''
        ---
        extends: relaxed

        rules:
          line-length: disable
      '';
    };

    ruff.enable = true;
    editorconfig-checker.enable = true;
  };

  # Make diffs fantastic
  difftastic.enable = true;

  # https://devenv.sh/integrations/dotenv/
  dotenv.enable = true;

  # https://devenv.sh/integrations/codespaces-devcontainer/
  devcontainer.enable = true;
}
