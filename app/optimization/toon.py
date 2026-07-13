try:
    from toon_format import encode, decode
except ImportError:
    encode = None
    decode = None

def encode_toon(data):
    important_fields = [
        "destination",
        "duration",
        "budget",
        "currency",
        "preferences"
    ]
    filtered_data = {field: data[field] for field in important_fields if data.get(field) is not None}
    
    if encode is not None:
        try:
            return encode(filtered_data)
        except NotImplementedError:
            pass

    # Robust fallback custom TOON representation
    lines = []
    for k, v in filtered_data.items():
        lines.append(f"{k}: {v}")
    return "\n".join(lines)

def decode_toon(toon_string):
    if decode is not None:
        try:
            return decode(toon_string)
        except NotImplementedError:
            pass

    # Robust fallback custom TOON parser
    data = {}
    for line in toon_string.strip().split("\n"):
        if ":" in line:
            k, v = line.split(":", 1)
            data[k.strip()] = v.strip()
    return data