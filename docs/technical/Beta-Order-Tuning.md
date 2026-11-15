# Draft order menu tuning

Run `python tools/build_order_tuning.py --display-key STRING_KEY --output generated-order-tuning` after replacing the string table key for **Order Life Journal**. The computer selector targets objects with the base-game `Purchase_Books_computer` affordance (99121), exported from the installed game, and places the action in the `computer_Order` category (98910). For a specific verified computer object tuning, pass `--computer-id COMPUTER_ID` instead. Repeat that option for multiple tunings.

The generator produces two interaction XML files that reference the shared order script class, plus one XML Injector snippet. The snippet adds the phone action to the phone affordance list and targets computers with the Purchase Books affordance for the computer action. Test XML Injector as a proposed dependency for this route. Computers lacking that affordance require an explicit object tuning ID.

Import the XML as tuning resources with their instance IDs, add the string table entry, and package the associated script. Validate phone category and availability on the installed patch and add any required phone-specific tuning. Check that each entry appears once. The generator produces draft XML only. In-game interaction visibility, household funds, runtime binding, and package loading remain to be verified.

[XML Injector modder documentation](https://scumbumbomods.com/xml-injector)
