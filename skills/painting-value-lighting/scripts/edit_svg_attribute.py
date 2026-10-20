from pathlib import Path
import argparse,xml.etree.ElementTree as ET
ET.register_namespace("", "http://www.w3.org/2000/svg")
ET.register_namespace("inkscape", "http://www.inkscape.org/namespaces/inkscape")
p=argparse.ArgumentParser(description="Edit one explicit SVG attribute without replacing the source")
p.add_argument("source",type=Path);p.add_argument("output",type=Path)
p.add_argument("--target",required=True);p.add_argument("--attr",required=True,choices=["fill","opacity","d","transform"]);p.add_argument("--value",required=True)
a=p.parse_args()
if a.output.exists():p.error("Output exists; choose a new revision path")
tree=ET.parse(a.source);nodes=[n for n in tree.iter() if n.get("id")==a.target]
if len(nodes)!=1:p.error("Target id must match exactly one node")
n=nodes[0];tag=n.tag.rsplit("}",1)[-1]
if a.attr=="d" and tag!="path":p.error("d edits require a path")
if a.attr=="fill" and list(n):p.error("Edit a leaf shape fill; children may override group fill")
if a.attr=="opacity":
 try:v=float(a.value)
 except ValueError:p.error("opacity must be numeric")
 if not 0<=v<=1:p.error("opacity must be between zero and one")
if n.get(a.attr)==a.value:p.error("No-op attribute edit")
old=n.get(a.attr);n.set(a.attr,a.value)
a.output.parent.mkdir(parents=True,exist_ok=True);tree.write(a.output,encoding="utf-8",xml_declaration=True)
print(f"{a.target}: {a.attr} {old!r} -> {a.value!r}; rendered effect still requires verification")
