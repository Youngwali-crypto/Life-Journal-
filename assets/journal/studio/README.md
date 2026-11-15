# Life Journal object import assets

Each prop has one triangulated OBJ mesh and a matching diffuse PNG. Import the OBJ into the Blender scene exported from a Sims 4 Studio object clone. Preserve the clone's required mesh groups, origin, scale and any required shadow or lower-detail meshes. Import the matching PNG as the diffuse texture in Studio. Use a placeable object for the parcel and an inventory-capable object for the planner.

The parcel uses OpenLifeJournalPackageInteraction and the planner uses OpenLifeJournalPlannerInteraction. Set their display names and wire their object definition IDs to JournalObjects after creating the two packages. Verify placement and inventory behavior in a disposable save.

These assets were exported from Blender 4.3.2. OBJ is the interchange format. Donor templates, game tuning, shadows, lower-detail resources and package imports still need validation on the target setup.
