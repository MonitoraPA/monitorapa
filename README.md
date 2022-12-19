# MonitoraPA
Monitoring system legal compliance (GDPR & all) of software systems

Telegram: https://t.me/monitoraPA   
[Element/Matrix](https://element.io): https://matrix.to/#/%23MonitoraPA:matrix.opencloud.lu

# Project Organization

MonitoraPA is composed of several components.

- A command line interface (in Python3) to run various automatic GDPR
  compliance checks on several systems (websites, email, cms...) and to automate
  some statistics and notifications to proper authorities in [cli/](./cli/),
  as specified in [ARCHITETTURA.md](./documentazione/ARCHITETTURA.md) and
  documented in [MANUALE.md](./documentazione/MANUALE.md)

- Some datasets to further extend the reach and impact of the project
  in [datasets/](./datasets/)

Further details are described in [ARCHITETTURA.md](./documentazione/ARCHITETTURA.md) (Italian).

# Authors, Copyright and Licensing

MonitoraPA has been created by several [AUTHORS](./AUTHORS.md).

It's brought to you under the [Hacking License](./LICENSE.txt) that, as
an explicit [shrink wrap contract](https://en.wikipedia.org/wiki/Shrink_wrap_contract) 
between you and the authors, must also be
applied to all dependant and derivative works (including the outputs
you produce running the system), recursively.

You cannot mix (A)GPL code with hacks covered by the Hacking License.

# Web Design

See the README.md in new repository https://github.com/MonitoraPA/web#design

# Coding Guidelines

Code like if your hack should be maintained by a child who
just learned how to code.

Do NOT try to solve problems that you haven't measured before.

Do NOT apply any "enterprise best practice". We are not a company.  
Do NOT try to show us how smart you are. We don't care.

Avoid dependencies.

Use good sense... but remember: it's not common.
