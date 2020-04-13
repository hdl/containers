from re import match
from graphviz import Digraph


class Stage(object):
    def __init__(self, name, parent):
        self._name = name
        self._from = parent
        self._copy = []

    @property
    def name(self):
        return self._name


def parse_dockerfile(dfile):
    stages = []
    curr = None
    with dfile.open() as fptr:
        content = fptr.read().splitlines()
        for l in content:
            if l[0:4] == "FROM":
                p = l[5:]
                n = "<empty>"
                for x in ["AS", "as"]:
                    x = " %s " % x
                    if x in p:
                        s = p.split(x)
                        p = s[0]
                        n = s[1]
                if curr:
                    stages += [curr]
                curr = Stage(
                    n,
                    p
                )
            #elif l[0:3] == "ARG":
            elif l[0:4] == "COPY":
                c = l[5:]
                if "--from=" in c:
                    curr._copy += [c[7:].split(" ")]
        if curr:
            stages += [curr]
        return stages

def generate_graph(stages):
    dot = Digraph(comment='OCI images maintained in ghdl/docker', filename="graph.gv", format="png")

    for k, v in stages.items():
        print()
        print(k)
        for i, s in enumerate(v):
            if (
                i == 0 or
                s._from in ("scratch", "alpine", "debian:buster-slim") or
                match(r'.*/.*:.*', s._from)
            ):
                kf = s._from.replace(':','__')
                kn = '%s%s' % (k, s.name)
                dot.node(kf, '%s' % s._from)
                dot.node(kn, '[%s] %s' % (k, s.name))
                dot.edge(kf, kn)
            else:
                kf = '%s%s' % (k, s._from.replace(':','__'))
                kn = '%s%s' % (k, s.name)
                dot.node(kf, '[%s] %s' % (k, s._from))
                dot.node(kn, '[%s] %s' % (k, s.name))
                dot.edge(kf, kn)
            print("STAGE from %s as %s" % (s._from, s.name))
            for c in s._copy:
                print("from", c[0], "copy", c[1], "to", c[2])

    #dot.edges(['AB', 'AL'])
    #dot.edge('B', 'L', constraint='false')

    #dot.view()