import json
def encode_toon(data):


    important_fields = [

        "destination",
        "duration",
        "budget",
        "currency",
        "preferences"

    ]


    output=[]


    for field in important_fields:

        value=data.get(field)


        if value:

            short_key = field[:3]


            output.append(
                f"{short_key}:{value}"
            )


    return "|".join(output)



def decode_toon(toon_string):

    data={}


    pairs = toon_string.split("|")


    for item in pairs:

        key,value=item.split(":",1)

        data[key]=value


    return data