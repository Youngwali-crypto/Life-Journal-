"""Generate draft interactions for the parcel and planner object clones."""
import argparse
from pathlib import Path
from xml.etree import ElementTree as ET

from build_order_tuning import resource_id, tuning_id


def build(output, parcel_tuning, planner_tuning, parcel_label, planner_label):
    if parcel_tuning == planner_tuning:
        raise ValueError("Parcel and planner require distinct object tuning IDs")
    if max(parcel_label, planner_label) >= 1 << 32:
        raise ValueError("String keys must fit in 32 bits")
    if parcel_label == planner_label:
        raise ValueError("Use separate string keys for the two action labels")

    output.mkdir(parents=True, exist_ok=True)
    name = "YoungwaliCrypto_LifeJournal_ObjectInjection"
    snippet = ET.Element("I", c="XmlInjector", i="snippet", m="xml_injector.snippet",
                         n=name, s=str(tuning_id(name)))
    objects = ET.SubElement(snippet, "L", n="add_interactions_to_objects")
    for prop, target, label in (("Package", parcel_tuning, parcel_label),
                                ("Planner", planner_tuning, planner_label)):
        action_name = "YoungwaliCrypto_LifeJournal_Open" + prop
        instance = str(tuning_id(action_name))
        action = ET.Element("I", c="OpenLifeJournal" + prop + "Interaction",
                            i="interaction", m="life_journal_delivery_interactions",
                            n=action_name, s=instance)
        ET.SubElement(action, "T", n="display_name").text = "0x{:08X}".format(label)
        ET.SubElement(action, "T", n="allow_autonomous").text = "False"
        ET.SubElement(action, "T", n="allow_user_directed").text = "True"
        ET.ElementTree(action).write(str(output / (action_name + ".xml")),
                                     encoding="utf-8", xml_declaration=True)

        entry = ET.SubElement(objects, "U")
        selector = ET.SubElement(entry, "V", n="object_selection", t="object_list")
        selector = ET.SubElement(selector, "U", n="object_list")
        targets = ET.SubElement(selector, "L", n="object_list")
        ET.SubElement(targets, "T").text = str(target)
        affordances = ET.SubElement(entry, "L", n="super_affordances")
        ET.SubElement(affordances, "T").text = instance
    ET.ElementTree(snippet).write(str(output / (name + ".xml")),
                                  encoding="utf-8", xml_declaration=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--parcel-tuning", required=True, type=resource_id)
    parser.add_argument("--planner-tuning", required=True, type=resource_id)
    parser.add_argument("--parcel-label", required=True, type=resource_id,
                        help="String key for Open Life Journal Package")
    parser.add_argument("--planner-label", required=True, type=resource_id,
                        help="String key for Open Life Journal")
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    try:
        build(args.output, args.parcel_tuning, args.planner_tuning,
              args.parcel_label, args.planner_label)
    except ValueError as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()
