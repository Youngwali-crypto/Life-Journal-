from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import Mock

from prototypes.game_context import home_context, sim_minutes


class GameContextTests(TestCase):
    def test_travel_home_move_and_save_identity(self):
        services = Mock()
        services.current_zone.return_value = SimpleNamespace(id=10)
        services.active_household.return_value = SimpleNamespace(id=20, home_zone_id=10)
        persistence = services.get_persistence_service.return_value
        persistence.get_save_slot_proto_guid.return_value = 30
        self.assertEqual(home_context(services), ("30", "20"))

        services.current_zone.return_value.id = 11
        self.assertIsNone(home_context(services))
        services.active_household.return_value.home_zone_id = 11
        self.assertEqual(home_context(services), ("30", "20"))

        persistence.get_save_slot_proto_guid.return_value = 31
        self.assertEqual(home_context(services), ("31", "20"))
        persistence.get_save_slot_proto_guid.return_value = 0
        self.assertIsNone(home_context(services))

    def test_clock_preserves_day_and_floors_subminute_ticks(self):
        services = Mock()
        ticks = services.time_service.return_value.sim_now.absolute_ticks
        ticks.return_value = 1980 * 25 - 1
        self.assertEqual(sim_minutes(services, 36000), 1979)
        ticks.return_value += 1
        self.assertEqual(sim_minutes(services, 36000), 1980)
