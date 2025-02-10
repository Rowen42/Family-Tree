import random
import string
import pandas as pd


# Generate a random 5 digit ID
def generate_random_id(existing_ids):

    while True:
        random_id = ''.join(random.choices(string.ascii_letters + string.digits, k=5))

        if random_id not in existing_ids:
            existing_ids.add(random_id)
            return random_id


# If a person does not have a randomly assigned ID in the 'ID' column, one will be assigned
def assign_ids(familytree):

    existing_ids = set(familytree['ID'].dropna())

    for index, row in familytree.iterrows():

        if pd.notna(row['Person']) and (pd.isna(row['ID'])) or row['ID'] == '':
            familytree.at[index, 'ID'] = generate_random_id(existing_ids)

    return familytree


def get_rid_of_numbers(familytree):

    familytree['Person'] = familytree['Person'].str.slice(start=1)

    return familytree
