from unittest import TestCase

from prototypes.journal_api import (
    JournalApiState,
    activate_mod,
    configure_settings,
    confirm_delivery,
    create_order,
    get_order,
    update_tracking,
)
from prototypes.journal_delivery_flow import (
    JournalOrderStatus as Status,
    JournalSettings,
    can_activate_life_journal_mod,
    simulate_delivery_timeline,
)


class JournalDeliveryTests(TestCase):
    def setUp(self):
        self.state = JournalApiState()
        self.order = create_order(self.state, "sim-1", "household-1", "Test address", "tracking-1")
        self.settings = JournalSettings("weekly", True, "private")

    def test_tracking_unlocks_activation_only_after_delivery(self):
        with self.assertRaises(ValueError):
            activate_mod(self.state, self.order.id)
        for stage in (Status.PROCESSING, Status.SHIPPED, Status.OUT_FOR_DELIVERY):
            order = update_tracking(self.state, "tracking-1", stage)
            self.assertEqual(order.status, stage)
            self.assertFalse(can_activate_life_journal_mod(order))

        delivered = update_tracking(self.state, "tracking-1", Status.DELIVERED)
        self.assertTrue(can_activate_life_journal_mod(delivered))
        self.assertFalse(delivered.mod_activated)
        with self.assertRaises(ValueError):
            configure_settings(self.state, self.order.id, self.settings)
        self.assertTrue(activate_mod(self.state, self.order.id).mod_activated)
        self.assertEqual(
            configure_settings(self.state, self.order.id, self.settings).settings, self.settings,
        )

    def test_manual_confirmation_and_carrier_retries_preserve_activation(self):
        delivered = confirm_delivery(self.state, self.order.id)
        activated = activate_mod(self.state, self.order.id)
        self.assertEqual(confirm_delivery(self.state, self.order.id), activated)
        self.assertEqual(update_tracking(self.state, "tracking-1", Status.DELIVERED), activated)
        self.assertEqual(update_tracking(self.state, "tracking-1", Status.SHIPPED), activated)
        self.assertEqual(get_order(self.state, self.order.id).delivered_at, delivered.delivered_at)

    def test_tracking_lookup_rejects_ambiguous_ids(self):
        self.assertIsNone(update_tracking(self.state, "unknown", Status.DELIVERED))
        with self.assertRaises(ValueError):
            create_order(self.state, "sim-2", "household-2", "Test address", "tracking-1")
        self.assertEqual(get_order(self.state, self.order.id), self.order)

    def test_timeline_preserves_original_order(self):
        timeline = simulate_delivery_timeline(self.order, (Status.SHIPPED, Status.DELIVERED))
        self.assertEqual([order.status for order in timeline], [
            Status.CREATED, Status.SHIPPED, Status.DELIVERED,
        ])
        self.assertEqual(get_order(self.state, self.order.id).status, Status.CREATED)
