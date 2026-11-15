"""Read the active home lot and absolute simulation time from game services."""


def home_context(services):
    zone = services.current_zone()
    household = services.active_household()
    persistence = services.get_persistence_service()
    if zone is None or household is None or persistence is None:
        return None
    if not household.id or not household.home_zone_id or zone.id != household.home_zone_id:
        return None
    save_guid = persistence.get_save_slot_proto_guid()
    if not save_guid or str(save_guid) == "0":
        return None
    return str(save_guid), str(household.id)


def sim_minutes(services, ticks_per_day):
    clock = services.time_service()
    if clock is None or ticks_per_day <= 0:
        raise ValueError("Simulation clock is unavailable")
    return clock.sim_now.absolute_ticks() * 1440 // ticks_per_day
