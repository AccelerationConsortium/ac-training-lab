# DB_utils.py used on HF space

import os
from datetime import datetime

import pandas as pd
from prefect import task
from pymongo import MongoClient

MONGODB_PASSWORD = os.getenv("MONGODB_PASSWORD")

blinded_connection_string = os.getenv("blinded_connection_string")

connection_string = blinded_connection_string.replace("<db_password>", MONGODB_PASSWORD)


@task
def generate_empty_well():
    dbclient = MongoClient(connection_string)
    db = dbclient["LCM-OT-2-SLD"]
    collection = db["wells"]
    rows = ["A", "B", "C", "D", "E", "F", "G", "H"]
    columns = [str(i) for i in range(1, 13)]
    for row in rows:
        for col in columns:
            well = f"{row}{col}"
            metadata = {"well": well, "status": "empty", "project": "OT2"}

            # send_data_to_mongodb(collection="wells", data=metadata)
            query = {"well": well}
            update_data = {"$set": metadata}
            collection.update_one(query, update_data, upsert=True)

    # close connection
    dbclient.close()


@task
def update_used_wells(used_wells):
    dbclient = MongoClient(connection_string)
    db = dbclient["LCM-OT-2-SLD"]
    collection = db["wells"]

    for well in used_wells:
        metadata = {"well": well, "status": "used", "project": "OT2"}
        # send_data_to_mongodb(collection="wells", data=metadata)
        query = {"well": well}
        update_data = {"$set": metadata}
        collection.update_one(query, update_data, upsert=True)

    # close connection
    dbclient.close()


@task
def find_unused_wells():
    dbclient = MongoClient(connection_string)
    db = dbclient["LCM-OT-2-SLD"]
    collection = db["wells"]
    query = {"status": "empty"}
    response = list(collection.find(query))
    df = pd.DataFrame(response)

    # Extract the "well" column as a list
    if "well" not in df.columns:
        raise ValueError("No available wells.")

    # Sort obtained list
    def well_sort_key(well):
        row = well[0]  # A, B, C, ...
        col = int(well[1:])  # 1, 2, ..., 12
        return (row, col)

    empty_wells = sorted(df["well"].tolist(), key=well_sort_key)
    # print(empty_wells)

    # close connection
    dbclient.close()

    # Check if there are any empty wells
    if len(empty_wells) == 0:
        raise ValueError("No empty wells found")
    # print(empty_wells)
    return empty_wells


@task
def save_result(result_data):
    dbclient = MongoClient(connection_string)
    db = dbclient["LCM-OT-2-SLD"]
    collection = db["MSE403_result"]  # change collection afte this practical finishes
    # collection = db["test_result"]
    result_data["timestamp"] = datetime.utcnow()  # UTC time
    insert_result = collection.insert_one(result_data)
    inserted_id = insert_result.inserted_id
    # close connection
    dbclient.close()
    return inserted_id


def get_student_quota(student_id):
    with MongoClient(connection_string) as client:
        db = client["LCM-OT-2-SLD"]
        collection = db["student"]
        student = collection.find_one({"student_id": student_id})
        if student is None:
            raise ValueError(f"Student ID '{student_id}' not found in the database.")
        return student.get("quota", 0)


def decrement_student_quota(student_id):
    dbclient = MongoClient(connection_string)
    db = dbclient["LCM-OT-2-SLD"]
    collection = db["student"]

    student = collection.find_one({"student_id": student_id})
    if not student:
        return f"Student ID {student_id} not found."
    if student.get("quota", 0) <= 0:
        return f"Student ID {student_id} has no remaining quota."

    result = collection.update_one(
        {"student_id": student_id, "quota": {"$gt": 0}}, {"$inc": {"quota": -1}}
    )

    if result.modified_count > 0:
        return f"Student ID {student_id}'s quota update successfully."
    else:
        return f"Quota update failed for Student ID {student_id}."


def add_student_quota(student_id, quota):
    """
    Adds a new student with a given quota.
    :param student_id: The ID of the student.
    :param quota: The initial quota for the student.
    """
    dbclient = MongoClient(connection_string)
    db = dbclient["LCM-OT-2-SLD"]
    collection = db["student"]
    student_data = {"student_id": student_id, "quota": quota}
    collection.update_one(
        {"student_id": student_id}, {"$set": student_data}, upsert=True
    )
    dbclient.close()


if __name__ == "__main__":
    generate_empty_well()
    # find_unused_wells()
    # test_id = "test"
    # quota = 999
    # add_student_quota(test_id, quota)
