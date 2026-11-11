# Draft order menu tuning

Run `python tools/build_order_tuning.py --computer-id COMPUTER_ID --display-key STRING_KEY --output generated-order-tuning` after replacing the capitalized values. Use the computer object tuning ID exported from your installed game, and the string table key for **Order Life Journal**. Supply additional verified computer object tuning IDs by repeating `--computer-id`.

The generator produces two interaction XML files that reference the shared order script class, plus one XML Injector snippet. The snippet adds the phone action to the phone affordance list and targets the specified computer tuning for the computer action. Test XML Injector as a proposed dependency for this route.

Import the XML as tuning resources with their instance IDs, add the string table entry, and package the associated script. Validate phone category and availability on the installed patch and add any required phone-specific tuning. Check that each entry appears once. The generator produces draft XML only. In-game interaction visibility, household funds, runtime binding, and package loading remain to be verified.

[XML Injector modder documentation](https://scumbumbomods.com/xml-injector)
