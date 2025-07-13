from lxml import etree
def parse_eu(path: str) -> list[dict]:
    root = etree.parse(path)
    ns = {"ns": root.getroot().nsmap[None]}
    return [
        {
          "name": alias.text,
          "program": "EU_FSF",
          "nationality": entry.findtext(".//ns:citizenship", namespaces=ns),
          "list_date": entry.findtext(".//ns:publication-date", namespaces=ns),
        }
        for entry in root.findall(".//ns:sanctions-entry", ns)
        for alias in entry.findall(".//ns:nameAlias/ns:wholeName", ns)
    ]