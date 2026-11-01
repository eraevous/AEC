# Security

AEC is a local, offline command-line tool. It reads files in the repository you point it at,
writes only to paths you name (or to `.aec/` with `aec init`), and makes no network requests.
It parses Python source with `ast` and never imports or runs the code it analyses. The only
subprocess it starts is `git config user.name`, during `aec init`, to name the owner stub.
`aec source` reads only the source roots configured in `.aec/sources.json` and refuses paths
outside them.

## Supported versions

Only the latest release receives fixes while AEC is pre-1.0.

## Reporting a vulnerability

Please do not open a public issue. Use GitHub's private vulnerability reporting
("Report a vulnerability" under the repository's Security tab), or contact the maintainer
through his GitHub profile. Expect an acknowledgement within a week.

Of particular interest: any way to make AEC read outside its configured roots, write
outside the paths it was given, execute code from the analysed repository, or make a
network request.
