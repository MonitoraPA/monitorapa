#!/usr/bin/env -S python3 -u

# This file is part of MonitoraPA
#
# Copyright (C) 2022 Marco Marinello <contact+nohuman@marinello.bz.it>
# Copyright (C) 2023 Giacomo Tesio <giacomo@tesio.it>
#
# MonitoraPA is a hack. You can use it according to the terms and
# conditions of the Hacking License (see LICENSE.txt)

from pathlib import Path
from datetime import datetime
import re
import sys

root = "."
target = "."

def dirname_to_isotime(dirname):
    date = dirname[0:10]
    hour = dirname[11:13]
    minute = dirname[13:15]
    second = dirname[15:17]
    return f"{date}T{hour}:{minute}:{second}"

class AtomEntry:
    def __init__(self, directory):
        cwd = root  # Path(Path(root).absolute())
        self.directory = directory
        self.text = f"In data {dirname_to_isotime(directory.name)} sono stati inviati dalla scuola {directory.parent.name} (provincia di "
        self.text += f"{directory.parent.parent.name.title()}) i seguenti file:"
        self.text += "\n<ul>"
        for attachment in [a for a in directory.glob("*") if a.is_file()]:
            #if "atom.xml" in attackment.name:
            #    continue
            self.text += f"\n<li><a href='https://foia.monitora-pa.it/{attachment.relative_to(cwd)}'>{attachment.name}</a>"
            self.text += "</li>"
        self.text += "</ul>"

    def export(self):
        return f"""<entry>
    <id>https://foia.monitora-pa.it/{self.directory.relative_to(root)}</id>
    <link type="text/html" rel="alternate" href="https://foia.monitora-pa.it/{self.directory.relative_to(root)}"/>
    <title>Risposta al FOIA da {self.directory.parent.name} del {dirname_to_isotime(self.directory.name)}</title>
    <updated>{dirname_to_isotime(self.directory.name)}</updated>
    <content type=\"html\"><p>{self.text}</p></content>
</entry>
"""


class AtomFeedElement:
    def __init__(self, path):
        self.root = path
        self.entries = []

    def build(self):
        print("building for", self.root)
        dirs = [a for a in self.root.glob("*") if a.is_dir()]
        if all([re.match("\d\d\d\d-\d\d-\d\d", a.name) for a in dirs]):
            for d in dirs:
                self.entries.append(AtomEntry(d))
            self.write_feed()
            return
        for d in dirs:
            _d = AtomFeedElement(d)
            _d.build()
            self.entries.append(_d)
        self.write_feed()

    def get_entries(self):
        e = [k for k in self.entries if type(k) == AtomEntry]
        for i in [k for k in self.entries if type(k) == AtomFeedElement]:
            e += i.get_entries()
        return sorted(e, key=lambda y: y.directory.name, reverse=True)

    def write_feed(self):
        print("write atom in", self.root / "atom.xml")
        with open(self.root / "atom.xml", "w") as hd:
            hd.write(self.gen_atom())

    def gen_atom(self):
        feed= f"""<?xml version="1.0"?>
<feed xmlns="http://www.w3.org/2005/Atom">

  <title>Monitora PA</title>
  <link href="https://foia.monitora-pa.it/{self.root.relative_to(root)}"/>
  <link type="application/atom+xml" rel="self" href="https://www.monitora-pa.it/atom.xml"/>
  <updated>{datetime.now().isoformat()}</updated>
  <id>https://foia.monitora-pa.it/{self.root.relative_to(root)}</id>
  <author>
    <name>Giacomo Tesio</name>
    <email>giacomo@tesio.it</email>
    <uri>http://www.tesio.it/</uri>
  </author>
  """
        for e in self.get_entries():
            feed += e.export()
        feed += "</feed>\n"
        return feed

def usage(argv):
    print(f"""
{argv[0]} site/root site/root/target

Crea un feed atom per la directory target/dir
(usare ./ per indicare la directory corrente)
""")
    sys.exit(-1)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        usage(sys.argv)
    root = Path(Path(sys.argv[1]).absolute())
    target = sys.argv[2]
    cwd = Path(Path(target).absolute())
    AtomFeedElement(cwd).build()
