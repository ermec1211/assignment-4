from pymongo import MongoClient
def obhectives():
    # Use a Local MongoDB Instance:
    # Your program must connect to a locally running MongoDB instance 
    # (mongodb://localhost:27017/).

    # You must create a MongoDB database for this project.

    # Dishes should be stored in a MongoDB collection of your choice.

    # The Program Must Be Capable Of:
    # Adding a New Dish

    # Each dish must have a name, calories, and ingredient list.

    # Dish names must be unique (i.e., no two dishes can have the
    # same name).

    # Showing All Dishes That Include a Particular Ingredient

    # The user should be able to input an ingredient and see all 
    # dishes that contain it.

    # Deleting a Particular Dish

    # The user should be able to remove a dish by entering its name.

    # If the dish does not exist, the program should notify the user.

    # Updating a Dish

    # The user should be able to update the calories or ingredient 
    # list of an existing dish.

    # The program must check that the dish exists before updating it.

    # Showing All Unique Ingredients in the Restaurant

    # The program should be able to retrieve and display a list 
    # of all unique ingredients across all dishes.

    # Showing All Dishes That Are Above or Below a Particular Calorie 
    # Threshold

    # The user should enter a calorie number and specify above or below.

    # The program should return all dishes matching the condition.

    # Program Structure & User Experience:
    # The program should prompt the user for actions through a 
    # menu-based system.

    # User input should be properly validated (e.g., avoid empty names, 
    # check for existing dishes before adding/updating/deleting).

    # The program should display clear messages after each operation 
    # (e.g., "Dish added successfully!", "No matching dishes found.").

    # Use Object Oriented principles as necessary to organize your 
    # code as needed. 
    pass


class DBManager:

    # inside this class, you should not have any user interaction
    # input or output
    # any value you require for insertion or update 
    # should be passed as parameter
    
    # any error you encounter, you should raise an exception
    # and let the caller handle it
    # in other words, do not print error messages
    
    client = MongoClient('mongodb://localhost:27017/')
    db = client['restaurant']
    dish_collection = db["dishes"]
    ingredient_collection = db["ingredients"]
    
    @staticmethod
    def add_dish(name, calories, ingredients):
        # check to see if ingredients already exist
        # any ingredient that does not exist is going to be 
        # added to the ingredient collection

        # insert the dish along with the ids of the appropriate ingredients
        # to the database.

        if (calories < 0):
            # this flips the table and throws an error
            # which the caller must catch
            raise Exception("calories cannot be negative")
        
        DBManager._check_dish_exists(name)

        all_ingredient_ids = DBManager.ingredient_manager(ingredients)
        dish = {
            "name": name,
            "calories": calories,
            "ingredients": all_ingredient_ids
        }
        DBManager.dish_collection.insert_one(dish)
        return dish


    @staticmethod
    def _if_dish_exists(dish_name):
        query = {"name": dish_name}
        result = DBManager.dish_collection.find_one(query)
        if result == None:
            raise Exception("Dish not found")
        
    @staticmethod
    def _check_dish_exists(dish_name):
        query = {"name": dish_name}
        result = DBManager.dish_collection.find_one(query)
        if result:
            raise Exception("dish already exists")
        

    @staticmethod
    def _get_ingredients(ingredient_names):
        # given a list of ingredeint names, return all ingredients that 
        # already exist in the database
        query = {"name": {"$in": ingredient_names}}
        ingredients = DBManager.ingredient_collection.find(query)
        return list(ingredients)


    @staticmethod
    def ingredient_manager(ingredients):
        # first check to see if any of the ingredients exist:
        existing_ingredients = DBManager._get_ingredients(ingredients)
        
        existing_ingredient_names = [ingredient["name"] for ingredient in existing_ingredients]
        existing_ingredient_ids = [ingredient["_id"] for ingredient in existing_ingredients]

        # go through each of the ingredients that we need to add and if they are not
        # already in the list of existing ingredients, then add them to the list
        # of ingredients to be created

        ingredients_to_add = []
        for ingredient in ingredients:
            if ingredient not in existing_ingredient_names:
                ingredients_to_add.append(ingredient)

        objects_to_insert = []
        for ingredient in ingredients_to_add:
            objects_to_insert.append({"name": ingredient})
        # add all the ingredients to the database in one go
        ids_inserted = DBManager.ingredient_collection.insert_many(
            objects_to_insert
        ).inserted_ids

        # get the ids of the ingredients that were just inserted
        # and add them to the list of existing ingredients
        all_ingredient_ids = existing_ingredient_ids + ids_inserted
        return all_ingredient_ids

    


    @staticmethod
    def _check_ingrediant_exists(ingredient_name):
        query = {"name": ingredient_name}
        result = DBManager.ingredient_collection.find(query)
        ingredents = list(result)
        ingredient = None
        if len(ingredents) > 0:
            ingredient = ingredents[0]
        if not ingredient:
            result = DBManager.ingredient_collection.insert_one(
                {"name": ingredient_name}
            )
            return result.inserted_id # this returns the id of the inserted ingredient
        else:
            return ingredient["_id"]
   


    @staticmethod
    def get_dishes_by_ingredient(ingredient_name):

        # get the id of the ingredient
        ingredient = DBManager._get_ingredient(ingredient_name)
        if not ingredient:
            return []
        
        ingredient_id = ingredient["_id"]

        # get all dishes that contain this ingredient
        # note that this matches both if the ingredients field
        # had a single objectId or if it was an array
        # in our case the ingredients field is an array
        # but this works to filter for all dishes that "contain" said
        # ingredient
        query = {"ingredients": ingredient_id}

        return list(DBManager.dish_collection.find(query))
        

    @staticmethod
    def delete_dish(name):
        query = {"name": name}
        result = DBManager.dish_collection.find_one(query)
        if result == None:
            raise Exception("Dish not found")
        else:
            DBManager.dish_collection.delete_one(query)
            return True
    

    @staticmethod
    def update_dish_name(current_name, new_name):
        DBManager._check_dish_exists(current_name)
        query = {"name": new_name}
        new_dish_name = DBManager.dish_collection.find_one(query)
        if new_dish_name != None:
            raise Exception("New dish name already exists")
        else:
            DBManager.dish_collection.update_one({"name": current_name}, {"$set": {"name": new_name}})
            return True
    

    @staticmethod
    def update_dish_calories(dish_name, new_calories):
        DBManager._check_dish_exists(dish_name)
        if new_calories < 0:
            raise Exception("Calories cannot be negative")
        DBManager.dish_collection.update_one({"name": dish_name}, {"$set": {"calories": new_calories}})
        return 
    

    @staticmethod
    def update_dish_ingredients(dish_name, new_ingredients):
        DBManager._if_dish_exists(dish_name)
    
        complete_list = DBManager.ingredient_manager(new_ingredients)

        DBManager.dish_collection.update_one({"name": dish_name}, {"$set": {"ingredients": complete_list}})
        return 

    @staticmethod
    def _get_ingredient(ingredient_name):
        query = {"name": ingredient_name}
        return DBManager.ingredient_collection.find_one(query)

    @staticmethod
    def get_all_unique_ingredients():
        ingredients = DBManager.ingredient_collection.find()
        return [ingredient["name"] for ingredient in ingredients]


    @staticmethod
    def get_dishes_above_calories(calorie):
        query = {"calories": {"$gt": calorie}}
        dishes = list(DBManager.dish_collection.find(query))
        return dishes


    @staticmethod
    def get_dishes_below_calories(calorie):
        query = {"calories": {"$lt": calorie}}
        dishes = list(DBManager.dish_collection.find(query))
        return dishes


    @staticmethod
    def get_ingredient_name_by_id(ingredient_id):
        ingredient = DBManager.ingredient_collection.find_one({"ingrediant_id": ingredient_id})
        return ingredient["name"] if ingredient else "Unknown"


class app:

    # write a function that adds a new dish
    # it is reponsible for interacting with the user

    @staticmethod
    def add_dish():
        # this method is reposible for interacting with the user
        # it should get the name, calories and ingredients
        # from the user
        # it should then call the DBManager.add_dish method
        # to add the dish to the database
        print("enter the name of the dish")
        dish_name = input()
        print("enter the calories of the dish")
        try:
            dish_calories = int(input())
        except ValueError:
            print("calories must be a number")
            return
        print("enter the ingredients of the dish separated by commas")
        dish_ingredients = input().split(",")
        try:
            DBManager.add_dish(dish_name, dish_calories, dish_ingredients)
        except Exception as e:
            print("sorry there was a problem adding your dish due to: ", e)
            return
        print("dish added!")


    @staticmethod
    def show_dishes_by_ingredient():
        print("enter the ingredient you want to search for")
        ingredient = input()
        dishes = DBManager.get_dishes_by_ingredient(ingredient)
        if not dishes:
            print("no dishes found")
        else:
            for dish in dishes:
                print(dish["name"])

    
    @staticmethod
    def delete_dish():
        name = input("Enter the name of the dish to delete: ").strip()
        if not name:
            print("Dish name cannot be empty.")
            return
        try:
            DBManager.delete_dish(name)
            print("Dish deleted successfully!")
        except Exception as e:
            print("Error deleting dish:", e)

    
    @staticmethod
    def update_dish():
        print("Enter the name of the dish you want to update")
        dish_name = input()

        print("What do you want to update?")
        print("1. Name")
        print("2. Calories")
        print("3. Ingredients")

        choice = input()

        if choice == "1":
            print("enter the new name")
            new_name = input()
            try:
                DBManager.update_dish_name(dish_name, new_name)
                print("Dish name updated successfully!")
            except Exception as e:
                print("Error updating dish name:", e)

        elif choice == "2":
            new_calories = input("Enter the new calories: ")
            try:
                DBManager.update_dish_calories(dish_name, int(new_calories))
                print("Dish calories updated successfully!")
            except Exception as e:
                print("Error updating dish calories:", e)

        elif choice == "3":
            print("Enter the new ingredients separated by commas: ")
            new_ingredients = input().split(",")
            try:
                DBManager.update_dish_ingredients(dish_name, new_ingredients)
                print("Dish ingredients updated successfully!")
            except Exception as e:
                print("Error updating dish ingredients:", e)

        else:
            print("Invalid choice")
    

    @staticmethod
    def show_all_unique_ingredients():
        ingredients = DBManager.get_all_unique_ingredients()
        for ingredient in ingredients:
            print(ingredient)

    
    @staticmethod
    def show_dishes_by_calories():
        print("Enter the calorie threshold")
        calorie = input()
        print("Do you want to see dishes above or below this calorie count?")
        print("1. Above")
        print("2. Below")
        choice = input()

        if choice == "1":
            dishes = DBManager.get_dishes_above_calories(int(calorie))
        elif choice == "2":
            dishes = DBManager.get_dishes_below_calories(int(calorie))
        else:
            print("Invalid choice")
            return
        
        if not dishes:
            print("No dishes found")
        else:
            for dish in dishes:
                print(dish["name"])


    @staticmethod
    def main():
        while True:
            print("welcome to the resturant")
            print("what would you like to do?")
            print("1. add a new dish")
            print("2. show all dishes that include a particular ingredient")
            print("3. delete a dish")
            print("4. update dish")
            print("5. show all unique ingredients in the restaurant")
            print("6. show all dishes that are above or below a calorie count")
            print("7. exit")

            choice = input()
            if choice == "1":
                app.add_dish()
            elif choice == "2":
                app.show_dishes_by_ingredient()
            elif choice == "3":
                app.delete_dish()
            elif choice == "4":
                app.update_dish()
            elif choice == "5":
                app.show_all_unique_ingredients()
            elif choice == "6":
                app.show_dishes_by_calories()
            elif choice == "7":
                break
            else:
                print("invalid choice")



if __name__ == "__main__":
    app.main()