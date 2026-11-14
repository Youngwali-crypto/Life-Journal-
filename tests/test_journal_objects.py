from unittest import TestCase
from unittest.mock import Mock

from life_journal_objects import JournalObjects


class JournalObjectsTests(TestCase):
    def test_apartment_drop_falls_back_when_door_is_unavailable(self):
        spawn = Mock()
        spawn.spawn_object_on_lot.return_value = object()
        objects = JournalObjects(1, 2, lambda *a: None, lambda key: None,
                                 lambda *a: None, lambda *a: None, lambda *a: False,
                                 spawn=spawn, inventory=Mock(),
                                 home_drop_location=lambda *a: 'inside apartment')
        self.assertEqual(objects.place_parcel_once('save', 'house', 'order'), 'order')
        self.assertEqual(spawn.spawn_object_on_lot.call_args.args[1], 'inside apartment')

    def test_house_drop_retries_inside_when_door_placement_fails(self):
        spawn = Mock()
        spawn.spawn_object_on_lot.side_effect = [None, object()]
        objects = JournalObjects(1, 2, lambda *a: 'door', lambda key: None,
                                 lambda *a: None, lambda *a: None, lambda *a: False,
                                 spawn=spawn, inventory=Mock(),
                                 home_drop_location=lambda *a: 'inside home')
        self.assertEqual(objects.place_parcel_once('save', 'house', 'order'), 'order')
        self.assertEqual([call.args[1] for call in spawn.spawn_object_on_lot.call_args_list],
                         ['door', 'inside home'])

    def test_order_marker_recovers_parcel_and_planner_without_spawning_again(self):
        spawn, inventory = Mock(), Mock()
        parcel, planner = object(), object()
        existing = {}
        spawn.spawn_object_on_lot.side_effect = lambda *args, **kw: (
            kw["on_object_initialize_callback"](parcel) or parcel)
        spawn.create_object.side_effect = lambda *args, **kw: (
            kw["on_object_initialize_callback"](planner) or planner)
        inventory.get_objects_in_inventory_by_definition_id_gen.side_effect = [[], [], [planner]]
        inventory.move_object_to_inventory.side_effect = [False, True]

        def mark(obj, key):
            existing[key] = obj

        objects = JournalObjects(1, 2, lambda *a: "porch", existing.get,
                                 lambda *a: "owner", mark,
                                 lambda obj, key: existing.get(key) is obj,
                                 spawn=spawn, inventory=inventory)
        self.assertEqual(objects.place_parcel_once("save", "house", "order"), "order")
        self.assertEqual(objects.place_parcel_once("save", "house", "order"), "order")
        spawn.spawn_object_on_lot.assert_called_once()
        self.assertFalse(objects.collect_journal_once("save", "sim", "order", "order"))
        spawn.destroy_object.assert_called_once()
        self.assertTrue(objects.collect_journal_once("save", "sim", "order", "order"))
        self.assertTrue(objects.collect_journal_once("save", "sim", "order", "order"))
        self.assertEqual(spawn.create_object.call_count, 2)
