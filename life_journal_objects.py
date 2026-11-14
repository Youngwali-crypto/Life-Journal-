"""Game object operations for the Journal delivery coordinator.

The bootstrap supplies custom object definitions, a safe porch location,
and order markers that survive game saves. Run these operations on the game thread.
"""


class JournalObjects:
    def __init__(self, parcel_definition, planner_definition, front_door_location,
                 find_parcel, resolve_sim, mark, matches, *, spawn=None, inventory=None):
        if (type(parcel_definition) is not int or type(planner_definition) is not int
                or min(parcel_definition, planner_definition) <= 0
                or parcel_definition == planner_definition):
            raise ValueError("Supply distinct parcel and planner definition IDs")
        if spawn is None:
            from sims4communitylib.utils.objects.common_object_spawn_utils import CommonObjectSpawnUtils
            spawn = CommonObjectSpawnUtils
        if inventory is None:
            from sims4communitylib.utils.sims.common_sim_inventory_utils import CommonSimInventoryUtils
            inventory = CommonSimInventoryUtils
        self.parcel_definition = parcel_definition
        self.planner_definition = planner_definition
        self.front_door_location = front_door_location
        self.find_parcel = find_parcel
        self.resolve_sim = resolve_sim
        self.mark = mark
        self.matches = matches
        self.spawn = spawn
        self.inventory = inventory

    def create_delivery(self, access):
        """Build the coordinator the home-lot bootstrap passes to bind_home_delivery."""
        from life_journal_notifications import show_delivery_notification
        from prototypes.journal_delivery import JournalDelivery

        return JournalDelivery(access, self.place_parcel_once, self.collect_journal_once,
                               remove_parcel=self.remove_parcel, notify=show_delivery_notification)

    def place_parcel_once(self, save_id, household_id, order_id):
        key = (save_id, order_id, "parcel")
        if self.find_parcel(key) is not None:
            return order_id
        location = self.front_door_location(save_id, household_id)
        if location is None:
            return None
        parcel = self.spawn.spawn_object_on_lot(
            self.parcel_definition, location,
            on_object_initialize_callback=lambda obj: self.mark(obj, key),
        )
        return order_id if parcel is not None else None

    def collect_journal_once(self, save_id, sim_id, order_id, parcel_id):
        if parcel_id != order_id:
            return False
        sim = self.resolve_sim(save_id, sim_id)
        if sim is None:
            return False
        key = (save_id, order_id, "planner", sim_id)
        for obj in self.inventory.get_objects_in_inventory_by_definition_id_gen(
                sim, self.planner_definition):
            if self.matches(obj, key):
                return True
        if self.find_parcel((save_id, order_id, "parcel")) is None:
            return False
        planner = self.spawn.create_object(
            self.planner_definition,
            on_object_initialize_callback=lambda obj: self.mark(obj, key),
        )
        if planner is None:
            return False
        if self.inventory.move_object_to_inventory(sim, planner):
            return True
        self.spawn.destroy_object(planner, cause="Life Journal inventory transfer failed")
        return False

    def remove_parcel(self, save_id, order_id, parcel_id):
        """Remove the marked box after its receipt has been saved."""
        if parcel_id != order_id:
            return
        key = (save_id, order_id, "parcel")
        parcel = self.find_parcel(key)
        if parcel is not None and self.matches(parcel, key):
            self.spawn.destroy_object(parcel, cause="Life Journal package collected")
