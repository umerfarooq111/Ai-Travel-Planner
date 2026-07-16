from app.memory.storage import load_profiles, save_profiles


def save_user_profile(profile):
    data = load_profiles()
    data[profile.user_id] = profile.model_dump()
    save_profiles(data)


def get_user_profile(user_id):
    data = load_profiles()
    return data.get(user_id)