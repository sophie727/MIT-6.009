"""
6.101 Lab 3:
Bacon Number
"""

#!/usr/bin/env python3

import pickle

# NO ADDITIONAL IMPORTS ALLOWED!

def get_key_from_val(dict, val):
    for k, v in dict.items():
        if v == val:
            return k
    return None
 
def transform_data(raw_data):
    return raw_data


def acted_together(transformed_data, actor_id_1, actor_id_2):
    raise NotImplementedError("Implement me!")


def actors_with_bacon_number(transformed_data, n):
    raise NotImplementedError("Implement me!") 


def bacon_path(transformed_data, actor_id):
    raise NotImplementedError("Implement me!")


def actor_to_actor_path(transformed_data, actor_id_1, actor_id_2):
    raise NotImplementedError("Implement me!")


def actor_path(transformed_data, actor_id_1, goal_test_function):
    raise NotImplementedError("Implement me!")


def actors_connecting_films(transformed_data, film1, film2):
    raise NotImplementedError("Implement me!")


if __name__ == "__main__":
    with open("resources/small.pickle", "rb") as f:
        smalldb = pickle.load(f)

    with open("resources/names.pickle", "rb") as f:
        names = pickle.load(f)

    print (names['Sven-Bertil Taube'])
    print (get_key_from_val(names, 27929))
    # additional code here will be run only when lab.py is invoked directly
    # (not when imported from test.py), so this is a good place to put code
    # used, for example, to generate the results for the online questions.
    pass
