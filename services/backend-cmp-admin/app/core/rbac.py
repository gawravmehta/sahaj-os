from app.core.security import rbac_enforcer


def reset_role_policies(role_id: str, routes: list):
    """
    Reset the policies for a given role_id to exactly the given `routes` list.
    routes: list of dicts like {"path": "/api/x", "actions": ["read","write"]}
    This function:
     - deduplicates requested rules
     - computes diff with current policies
     - removes only policies that should be removed
     - adds only policies that should be added
     - saves policy once at end (since auto_save is disabled)
    """

    desired = set()
    for route in routes or []:
        path = route.get("path")
        if not path:
            continue
        actions = route.get("actions") or []

        for act in set(actions):
            desired.add((str(role_id), str(path), str(act)))

    current = set()

    cur_policies = rbac_enforcer.get_filtered_policy(0, role_id)
    for p in cur_policies:

        if len(p) >= 3:
            current.add((str(p[0]), str(p[1]), str(p[2])))

    to_add = desired - current
    to_remove = current - desired

    for sub, obj, act in to_remove:

        rbac_enforcer.remove_policy(sub, obj, act)

    for sub, obj, act in to_add:

        if not rbac_enforcer.has_policy(sub, obj, act):
            rbac_enforcer.add_policy(sub, obj, act)

    rbac_enforcer.save_policy()
