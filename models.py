import json
import os

import dotenv
from neo4j import GraphDatabase
from neo4j.graph import Node

dotenv.load_dotenv("Neo4j-54eecc8b-Created-2023-12-10.txt")

driver = GraphDatabase.driver(
    os.getenv("NEO4J_URI"),
    auth=(os.getenv("NEO4J_USERNAME"), os.getenv("NEO4J_PASSWORD")),
    database="neo4j")


# def get():
#     records, summary, keys = driver.execute_query(
#         "MATCH (p:Person) RETURN p.name AS name",
#         database_="neo4j",
#     )

#     # Loop through results and do something with them
#     for record in records:
#         print("record", record.data())  # obtain record as dict

#     # Summary information
#     print("The query `{query}` returned {records_count} records in {time} ms.".format(
#         query=summary.query, records_count=len(records),
#         time=summary.result_available_after
#     ))

#     return str(records)


class Dish:
    def __init__(self, name) -> None:
        self.name = name.replace("_", " ")

    def get_contains(self):
        result = {}

        records, summary, keys = driver.execute_query(
            """
            MATCH (dish:Dish {name: $name})-[:CONTAINS]->(sub:Ingredient)
            RETURN sub
            """,
            name=self.name
        )
        result["ingredients"] = [record.value().get("name", None) for record in records]

        records, summary, keys = driver.execute_query(
            """
            MATCH (dish:Dish {name: $name})-[:CONTAINS]->(sub:Dish)
            RETURN sub
            """,
            name=self.name
        )
        result["subdishes"] = [record.value().get("name", None) for record in records]

        records, summary, keys = driver.execute_query(
            """
            MATCH (dish:Dish)-[:CONTAINS]->(sub:Dish {name: $name})
            RETURN dish
            """,
            name=self.name
        )
        result["in_dishes"] = [record.value().get("name", None) for record in records]

        return result

    def delete(self):
        driver.execute_query(
            """
            MATCH (d:Dish {name: $name})
            OPTIONAL MATCH (d)-[r1]->()
            OPTIONAL MATCH ()-[r2]->(d)
            DELETE r1
            DELETE r2
            DELETE d
            """,
            name = self.name
        )


class Ingredient:
    def __init__(self, name: str) -> None:
        self.name = name.replace("_", " ")

    @staticmethod
    def get_all():
        query = """
        MATCH (ing:Ingredient)
        RETURN ing
        """
        records, summary, keys = driver.execute_query(query)
        return [record.value().get("name", None) for record in records]

    def get_dishes(self):
        records, summary, keys = driver.execute_query(
            """
            MATCH (d:Dish)-[:CONTAINS]->(i:Ingredient {name: $name})
            RETURN d, [(d)-[:IS]->(t:DishType) | t.type] AS types
            """,
            name=self.name
        )

        return [{
            "name": record.value().get("name"),
            "types": record.value(1)
        } for record in records]


class Connection:
    def __init__(self, dish_name, dish_type) -> None:
        self.dish_name = dish_name
        self.dish_type = dish_type
        self.contain = []

    def add_subdish(self, subdish_name):
        self.contain.append(Dish(subdish_name))

    def add_ingredient(self, ingredient_name):
        self.contain.append(Ingredient(ingredient_name))

    def save(self):
        def action(tx):
            tx.run(
                "MERGE (:Dish {name: $name})",
                name=self.dish_name
            )

            if self.dish_type is not None:
                tx.run(
                    """
                    MATCH (d:Dish {name: $name})
                    MERGE (t:DishType {type: $type})
                    MERGE (d)-[:IS]->(t)
                    """,
                    name=self.dish_name,
                    type=self.dish_type
                )

            for item in self.contain:
                if type(item) == Dish:
                    tx.run(
                        """
                        MATCH (d:Dish {name: $name})
                        MERGE (d2:Dish {name: $subdish})
                        MERGE (d)-[:CONTAINS]->(d2)
                        """,
                        name=self.dish_name,
                        subdish=item.name
                    )
                elif type(item) == Ingredient:
                    tx.run(
                        """
                        MATCH (d:Dish {name: $name})
                        MERGE (i:Ingredient {name: $ingredient})
                        MERGE (d)-[:CONTAINS]->(i)
                        """,
                        name=self.dish_name,
                        ingredient=item.name
                    )
                else:
                    raise TypeError

        with driver.session() as session:
            session.execute_write(action)
