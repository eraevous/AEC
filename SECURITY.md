# Security

Telosmith is a local, offline command-line tool. It reads files in the repository you point it at,
writes only to paths you name (or to `.aec/` with `aec init`), and makes no network requests.
It parses Python source with `ast` and never imports or runs the code it analyses. The only
subprocess it starts is `git config user.name`, during `aec init`, to name the owner stub.
`aec source` reads only the source roots configured in `.aec/sources.json` and refuses paths
outside them.

## Supported versions

Only the latest release receives fixes while Telosmith is pre-1.0.

## Reporting a vulnerability

Please do not put details in a public issue. Open an issue titled "Security contact request" with no
details, and the maintainer will arrange a private channel. If the repository's Security tab shows
"Report a vulnerability", use that instead: it goes straight to the maintainer privately.

The tool itself makes no network requests. The install command and the CI job that `aec init`
generates do download packages (pip, GitHub Actions); that is the installer's network use, not Telosmith's.

Of particular interest: any way to make Telosmith read outside its configured roots, write outside the paths
it was given, execute code from the analysed repository, or make a network request.
