from app.memory.preferences import get_user_profile, save_user_profile
from app.memory.profile import UserProfile


def preference_node(state):
    user_id = state["user_id"]
    profile = get_user_profile(user_id)

    if profile:
        profile.setdefault("favorite_destinations", [])
        profile.setdefault("interests", [])

        if state.get("destination") and state["destination"] not in profile["favorite_destinations"]:
            profile["favorite_destinations"].append(state["destination"])

        if state.get("budget"):
            profile["average_budget"] = state["budget"]

        if state.get("preferences"):
            profile["travel_style"] = state["preferences"]

        if state.get("currency"):
            profile["preferred_currency"] = state["currency"]

        save_user_profile(UserProfile(**profile))
        return {"user_profile": profile}

    profile = UserProfile(
        user_id=user_id,
        travel_style=state.get("preferences") or "",
        preferred_transport="",
        preferred_accommodation="",
        favorite_destinations=[state["destination"]] if state.get("destination") else [],
        interests=[],
        average_budget=state.get("budget") or 0,
        preferred_currency=state.get("currency") or "PKR",
    )

    save_user_profile(profile)
    return {"user_profile": profile.model_dump()}
