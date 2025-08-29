from faker import Faker
fake = Faker()

from datetime import datetime

dbname = lambda: "cdr"
collection_name = lambda: "logs"

from pymongo import IndexModel, ASCENDING

def create_indexes(coll):
    indexes = [
        IndexModel([("contract", ASCENDING)]),
        IndexModel([('subtype_code', ASCENDING)]),
        IndexModel([('date', ASCENDING)], name='ttl_date_1', expireAfterSeconds=365*24*60*60),
        IndexModel([('properties.caller', ASCENDING), ('properties.callee', ASCENDING)], sparse=True),
        IndexModel([('properties.device', ASCENDING)], sparse=True),
        IndexModel([('properties.app', ASCENDING)], sparse=True),
        IndexModel([('properties.network_type', ASCENDING)], sparse=True),
    ]
    coll.create_indexes(indexes)

def generate_log():
    categories = ["VOICE", "SMS", "MMS", "DATA"]
    subtypes = {
        "VOICE": ["INBOUND", "OUTBOUND"],
        "SMS": ["INBOUND", "OUTBOUND"],
        "MMS": ["INBOUND", "OUTBOUND"],
        "DATA": ["BASIC", "PLUS", "PREMIUM", "SUPER", "ULTRA"],
    }

    def prop_voice():
        return {
            'caller': fake.phone_number(),
            'callee': fake.phone_number(),
            'call_quality': fake.random_element(elements=["DD", "HH", "HD"])
        }

    def prop_data():
        return {
            'device': fake.random_element(elements=["Samsung A", "Samsung S", "iPhone", "Huawei"])
                + str(fake.random_int(min=1, max=20)),
            'app': fake.random_element(elements=["Facebook", "Instagram", "Twitter", "Snapchat", "YouTube", "Netflix"]),
            'network_type': fake.random_element(elements=["LTE", "5G", "WiFi"])
        }

    props = {
        "VOICE": prop_voice,
        "SMS": prop_voice,
        "MMS": prop_voice,
        "DATA": prop_data
    }

    category = fake.random_element(elements=categories)
    subtype = fake.random_element(elements=subtypes[category])

    T_STR = "%H:%M:%S"
    start_time = fake.date_time_between(
        start_date=datetime.strptime("00:00:00", T_STR),
        end_date=datetime.strptime("23:59:59", T_STR)
    )
    end_time = fake.date_time_between(
        start_date=start_time,
        end_date=datetime.strptime("23:59:59", T_STR)
    )
    usage = int(end_time.timestamp() - start_time.timestamp())
    return {
        "category": category,
        "subtype_code": subtype,
        "start_time": start_time.strftime('%H:%M:%S'),
        "end_time": end_time.strftime('%H:%M:%S'),
        "usage": usage,
        "properties": props[category]()
    }

def generate_doc(contract, date):
    return {
        "contract": contract,
        "date": date,
        **generate_log(),
    }

def generate_docs(N):
    START = 11111111
    for n in range(START, START + N):
        contract = '010-' + str(n)[:4] + '-' + str(n)[4:]
        nDocs = fake.random_int(min=1, max=200)

        docs = []
        date = fake.date_time_between(start_date="-1y", end_date="now")
        for _ in range(nDocs):
            docs.append(generate_doc(contract, date))
        yield docs