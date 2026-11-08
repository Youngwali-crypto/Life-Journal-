"""Optional S4CL-backed skill reader; not an installed or auto-running mod.

The bootstrap must supply verified loaded-save context and absolute Sim minutes.
Imports stay lazy so the outside-game prototype requires no S4CL installation.
"""
import math


class S4CLSkillReader:
    def __init__(self, sim_utils=None, household_utils=None, skill_utils=None):
        if sim_utils is None:
            from sims4communitylib.utils.sims.common_sim_utils import CommonSimUtils
            sim_utils = CommonSimUtils
        if household_utils is None:
            from sims4communitylib.utils.sims.common_household_utils import CommonHouseholdUtils
            household_utils = CommonHouseholdUtils
        if skill_utils is None:
            from sims4communitylib.utils.sims.common_sim_skill_utils import CommonSimSkillUtils
            skill_utils = CommonSimSkillUtils
        self.sims = sim_utils
        self.households = household_utils
        self.skills = skill_utils

    def observe(self, bridge, context, objective_id, skill_id, now):
        if type(skill_id) is not int or skill_id <= 0:
            raise ValueError('Use a verified positive skill tuning ID')
        bridge._check(context)
        sim_info = self.sims.get_sim_info(int(context.sim_id))
        if sim_info is None:
            return 'unavailable'
        if (str(self.sims.get_sim_id(sim_info)) != context.sim_id or
                str(self.households.get_household_id(sim_info)) != context.household_id):
            raise ValueError('Sim identity or household changed; reconcile selection')
        # add=False makes monitoring read-only. Missing skills produce no credit.
        skill = self.skills.get_skill(sim_info, skill_id, add=False)
        if skill is None:
            return 'unavailable'
        level = self.skills.get_current_skill_level(
            sim_info, skill_id, use_effective_skill_level=False,
        )
        if isinstance(level, bool) or not isinstance(level, (float, int)) or not math.isfinite(level) or level < 0:
            raise ValueError('Invalid skill level from game')
        return bridge.observe_skill(context, objective_id, math.floor(level), now)
