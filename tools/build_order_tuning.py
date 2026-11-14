"""Generate reviewable Life Journal tuning XML for import into a package."""
import argparse
from pathlib import Path
from xml.etree import ElementTree as ET


def tuning_id(name):
    value = 14695981039346656037
    for byte in name.encode("ascii"):
        value = ((value * 1099511628211) ^ byte) & 0xFFFFFFFFFFFFFFFF
    return value | (1 << 63)


def build(output, computer_ids, display_key):
    output.mkdir(parents=True, exist_ok=True)
    names = {surface: "YoungwaliCrypto_LifeJournal_Order_" + surface
             for surface in ("Phone", "Computer")}
    ids = {surface: tuning_id(name) for surface, name in names.items()}
    for surface, name in names.items():
        action = ET.Element("I", c="OrderLifeJournalInteraction", i="interaction",
                            m="life_journal_order_interaction", n=name, s=str(ids[surface]))
        ET.SubElement(action, "T", n="display_name").text = "0x{:08X}".format(display_key)
        if surface == "Computer":
            ET.SubElement(action, "T", n="category").text = "98910"
        ET.SubElement(action, "T", n="allow_autonomous").text = "False"
        ET.SubElement(action, "T", n="allow_user_directed").text = "True"
        ET.ElementTree(action).write(str(output / (name + ".xml")), encoding="utf-8", xml_declaration=True)

    name = "YoungwaliCrypto_LifeJournal_OrderInjection"
    snippet = ET.Element("I", c="XmlInjector", i="snippet", m="xml_injector.snippet",
                         n=name, s=str(tuning_id(name)))
    phones = ET.SubElement(snippet, "L", n="add_interactions_to_phones")
    ET.SubElement(phones, "T").text = str(ids["Phone"])
    objects = ET.SubElement(snippet, "L", n="add_lock_aware_interactions_to_lockable_objects")
    entry = ET.SubElement(objects, "U")
    if computer_ids:
        selection = ET.SubElement(entry, "V", n="object_selection", t="object_list")
        selection = ET.SubElement(selection, "U", n="object_list")
        targets = ET.SubElement(selection, "L", n="object_list")
        for object_id in sorted(set(computer_ids)):
            ET.SubElement(targets, "T").text = str(object_id)
    else:
        selection = ET.SubElement(entry, "V", n="object_selection", t="objects_with_tag")
        selection = ET.SubElement(selection, "U", n="objects_with_tag")
        ET.SubElement(selection, "E", n="tag").text = "Func_Computer"
    affordances = ET.SubElement(entry, "L", n="super_affordances")
    ET.SubElement(affordances, "T").text = str(ids["Computer"])
    ET.ElementTree(snippet).write(str(output / (name + ".xml")), encoding="utf-8", xml_declaration=True)


def resource_id(value):
    try:
        number = int(value, 0)
    except ValueError:
        raise argparse.ArgumentTypeError("Expected a decimal or 0x hexadecimal resource ID")
    if not 0 < number < 1 << 64:
        raise argparse.ArgumentTypeError("Resource ID must be a positive 64-bit integer")
    return number


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--computer-id", action="append", type=resource_id,
                        help="Optional verified computer object tuning ID. Repeat for multiple tunings.")
    parser.add_argument("--display-key", required=True, type=resource_id,
                        help="String table key for Order Life Journal.")
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    if args.display_key >= 1 << 32:
        parser.error("--display-key must fit in 32 bits")
    build(args.output, args.computer_id, args.display_key)


if __name__ == "__main__":
    main()
