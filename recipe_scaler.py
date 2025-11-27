import json
import os

# Common ingredient densities (g/ml for volume to weight conversions)
INGREDIENT_DENSITY = {
    # Dry ingredients (g/cup unless specified)
    'all-purpose flour': 125,
    'sugar': 200,
    'brown sugar': 220,
    'powdered sugar': 120,
    'butter': 227,  # 1 cup = 227g
    'chocolate chips': 170,
    'cocoa powder': 100,
    'oats': 90,
    'rice': 200,
    'pasta': 200,
    'bread crumbs': 100,
    'chopped nuts': 120,
    'grated cheese': 100,
    
    # Common liquids (g/ml)
    'water': 1,
    'milk': 1.03,
    'oil': 0.92,
    'honey': 1.42,
    'maple syrup': 1.33,
    'yogurt': 1.03,
    'heavy cream': 0.994
}

# Common ingredient densities (g per cup)
INGREDIENT_DENSITY = {
    'flour': 125,          # All-purpose flour
    'sugar': 200,          # Granulated sugar
    'brown sugar': 220,    # Packed brown sugar
    'butter': 227,         # 1 cup = 2 sticks = 227g
    'chocolate chips': 175,
    'milk': 240,           # 1 cup = 240ml = ~240g
    'oil': 215,            # Most cooking oils
    'honey': 340,          # 1 cup honey
    'oats': 90,            # Rolled oats
    'rice': 200,           # Uncooked white rice
    'pasta': 100,          # Uncooked pasta
    'cheese': 113,         # Grated cheddar
    'yogurt': 245,         # Plain yogurt
    'cream': 240,          # Heavy cream
    'water': 236.588       # 1 cup = 236.588ml
}

# Conversion factors (volume in tablespoons, weight in grams)
CONVERSIONS = {
    # Volume conversions (tbsp as base)
    'tbsp': {'tsp': 3, 'cup': 1/16, 'pint': 1/32, 'quart': 1/64, 'liter': 0.0147868, 'ml': 14.7868},
    'tsp': {'tbsp': 1/3, 'cup': 1/48, 'pint': 1/96, 'quart': 1/192, 'liter': 0.00492892, 'ml': 4.92892},
    'cup': {'tbsp': 16, 'tsp': 48, 'pint': 0.5, 'quart': 0.25, 'liter': 0.236588, 'ml': 236.588},
    'pint': {'tbsp': 32, 'tsp': 96, 'cup': 2, 'quart': 0.5, 'liter': 0.473176, 'ml': 473.176},
    'quart': {'tbsp': 64, 'tsp': 192, 'cup': 4, 'pint': 2, 'liter': 0.946353, 'ml': 946.353},
    'liter': {'tbsp': 67.628, 'tsp': 202.884, 'cup': 4.22675, 'pint': 2.11338, 'quart': 1.05669, 'ml': 1000},
    'ml': {'tbsp': 0.067628, 'tsp': 0.202884, 'cup': 0.00422675, 'pint': 0.00211338, 'quart': 0.00105669, 'liter': 0.001},
    
    # Weight conversions (grams as base)
    'g': {'kg': 0.001, 'oz': 0.035274, 'lb': 0.00220462},
    'kg': {'g': 1000, 'oz': 35.274, 'lb': 2.20462},
    'oz': {'g': 28.3495, 'kg': 0.0283495, 'lb': 0.0625},
    'lb': {'g': 453.592, 'kg': 0.453592, 'oz': 16}
}

def load_recipes():
    """Load recipes from recipes.json file."""
    try:
        with open('recipes.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print("Error: recipes.json file not found.")
        return []
    except json.JSONDecodeError:
        print("Error: Invalid JSON format in recipes.json.")
        return []

def scale_recipe(recipe, new_servings):
    """
    Scale the recipe to a new number of servings with practical measurements.
    
    Args:
        recipe (dict): The recipe to scale
        new_servings (int): The desired number of servings
        
    Returns:
        dict: The scaled recipe or None if invalid input
    """
    if not recipe or new_servings <= 0:
        print("Error: Invalid recipe or serving size.")
        return None
        
    if 'servings' not in recipe or 'ingredients' not in recipe:
        print("Error: Invalid recipe format.")
        return None
        
    # Create a deep copy to avoid modifying the original
    scaled_recipe = recipe.copy()
    scaled_recipe['ingredients'] = [ingredient.copy() for ingredient in recipe['ingredients']]
    
    # Calculate scaling factor
    scale_factor = new_servings / recipe['servings']
    scaled_recipe['servings'] = new_servings
    
    # Common conversions for better readability
    conversions = {
        'cup': {
            'tbsp': 16,
            'tsp': 48
        },
        'tbsp': {
            'tsp': 3
        }
    }
    
    # Scale each ingredient
    for ingredient in scaled_recipe['ingredients']:
        # Calculate scaled amount
        scaled_amount = ingredient['amount'] * scale_factor
        unit = ingredient['unit']
        
        # Handle different unit types
        if unit == 'piece':
            # For pieces, just round to nearest 0.25
            ingredient['amount'] = round(scaled_amount * 4) / 4
        elif unit in ['cup', 'tbsp', 'tsp']:
            # For volume measurements, convert to most appropriate unit
            if unit == 'cup' and scaled_amount < 0.25:
                # Convert to tablespoons
                tbsp = scaled_amount * 16
                if tbsp >= 1:
                    ingredient['amount'] = round(tbsp, 1)
                    ingredient['unit'] = 'tbsp'
                    continue
                else:
                    # Convert to teaspoons
                    tsp = tbsp * 3
                    ingredient['amount'] = round(tsp, 1)
                    ingredient['unit'] = 'tsp'
                    continue
            elif unit == 'tbsp' and scaled_amount < 0.5:
                # Convert to teaspoons
                tsp = scaled_amount * 3
                ingredient['amount'] = round(tsp, 1)
                ingredient['unit'] = 'tsp'
                continue
            else:
                # Round to 2 decimal places for cups, 1 for others
                ingredient['amount'] = round(scaled_amount, 2 if unit == 'cup' else 1)
        elif unit in ['g', 'ml']:
            # For metric, round to nearest whole number
            ingredient['amount'] = round(scaled_amount)
        else:
            # For other units, just scale and round to 1 decimal
            ingredient['amount'] = round(scaled_amount, 1)
    
    return scaled_recipe

def convert_units(amount, unit, target_unit):
    """
    Convert an amount from one unit to another if they are compatible.
    
    Args:
        amount (float): The amount to convert
        unit (str): The current unit
        target_unit (str): The unit to convert to
        
    Returns:
        tuple: (converted_amount, target_unit) if successful, (None, None) otherwise
    """
    if unit == target_unit:
        return amount, target_unit
        
    # Check if units are in the same category (volume or weight)
    volume_units = {'tbsp', 'tsp', 'cup', 'pint', 'quart', 'liter', 'ml'}
    weight_units = {'g', 'kg', 'oz', 'lb'}
    
    unit = unit.lower()
    target_unit = target_unit.lower()
    
    if (unit in volume_units and target_unit in volume_units) or \
       (unit in weight_units and target_unit in weight_units):
        try:
            converted = amount * CONVERSIONS[unit][target_unit]
            return round(converted, 2), target_unit
        except KeyError:
            pass
            
    return None, None

def get_best_unit(ingredient_name, amount, current_unit):
    """Convert to the most appropriate unit (g for dry, ml for liquids, or best volume unit)."""
    # First, check if we can convert to weight (grams)
    ingredient_lower = ingredient_name.lower()
    
    # Skip conversion for these ingredients
    skip_conversion = ['garlic', 'ginger', 'onion', 'pepper', 'salt', 'baking powder', 
                      'baking soda', 'yeast', 'spices', 'herbs', 'vanilla extract', 'extract']
    
    if any(skip in ingredient_lower for skip in skip_conversion):
        return amount, current_unit
    
    # Try to convert to grams for dry ingredients
    if current_unit in ['cup', 'tbsp', 'tsp', 'pint', 'quart', 'liter', 'ml']:
        # Check if we have density information for this ingredient
        for key, density in INGREDIENT_DENSITY.items():
            if key in ingredient_lower:
                # Convert to ml first if needed
                if current_unit == 'cup':
                    ml = amount * 236.588
                elif current_unit == 'tbsp':
                    ml = amount * 14.7868
                elif current_unit == 'tsp':
                    ml = amount * 4.92892
                else:
                    ml = amount  # already in ml or not convertible
                
                # Convert to grams using density
                grams = round(ml * density, 1)
                if grams >= 1:  # Only convert if it's at least 1g
                    return grams, 'g'
                break
    
    # If we can't convert to grams, try to use the most appropriate volume unit
    if current_unit == 'cup' and amount < 0.25:
        tbsp = amount * 16
        if tbsp >= 1:
            return round(tbsp, 1), 'tbsp'
    
    if current_unit == 'tbsp' and amount < 1:
        tsp = amount * 3
        if tsp >= 1:
            return round(tsp, 1), 'tsp'
    
    return amount, current_unit

def format_measurement(amount, unit, name):
    """Format the measurement in the most readable way."""
    # Handle pieces
    if unit == 'piece':
        if amount < 1:
            # Convert to fraction for pieces less than 1
            fraction = round(amount * 4) / 4
            parts = str(fraction).split('.')
            if len(parts) > 1 and parts[1] != '0':
                frac_map = {'25': '1/4', '5': '1/2', '75': '3/4'}
                frac_part = frac_map.get(parts[1][:2], '')
                if frac_part:
                    return f"{int(parts[0]) if parts[0] != '0' else ''} {frac_part}".strip()
        return f"{int(amount) if amount.is_integer() else amount:.1f}"
    
    # For other units, round to 1 decimal place if needed
    if unit in ['g', 'ml']:
        return f"{int(amount) if amount.is_integer() else amount:.1f}"
    
    # For volume units, use fractions for small amounts
    if unit == 'tsp' and amount < 1 and not amount.is_integer():
        fraction = round(amount * 4) / 4
        parts = str(fraction).split('.')
        if len(parts) > 1 and parts[1] != '0':
            frac_map = {'25': '1/4', '5': '1/2', '75': '3/4'}
            frac_part = frac_map.get(parts[1][:2], '')
            if frac_part:
                return f"{int(parts[0]) if parts[0] != '0' else ''} {frac_part}".strip()
    
    return f"{int(amount) if amount.is_integer() else amount:.1f}"

def convert_cups_to_grams(ingredient_name, amount):
    """Convert volume in cups to grams based on ingredient type."""
    ingredient_name = ingredient_name.lower()
    
    # Find the best matching ingredient in our density table
    for key, density in INGREDIENT_DENSITY.items():
        if key in ingredient_name:
            return round(amount * density)
    
    # Default to flour density if no match found
    return round(amount * 125)

def display_recipe(recipe):
    """Display the recipe in a clean, easy-to-read format with cups converted to grams."""
    if not recipe:
        return
        
    print(f"\n{recipe['name']} (Serves {recipe['servings']})")
    print("-" * 40)
    
    for ingredient in recipe['ingredients']:
        amount = ingredient['amount']
        unit = ingredient['unit']
        name = ingredient['name']
        
        # Format the amount based on unit type
        if unit == 'piece':
            # For pieces, show as whole numbers or fractions
            if amount < 1:
                # Convert to fraction
                fraction = round(amount * 4) / 4  # Round to nearest 1/4
                parts = str(fraction).split('.')
                if len(parts) > 1 and parts[1] != '0':
                    frac_map = {'25': '1/4', '5': '1/2', '75': '3/4'}
                    frac_part = frac_map.get(parts[1][:2], '')
                    if frac_part:
                        print(f"- {frac_part} {name}")
                        continue
            print(f"- {int(amount) if amount == int(amount) else amount} {name}")
            
        elif unit == 'cup':
            # Convert cups to grams
            grams = convert_cups_to_grams(name, amount)
            print(f"- {grams}g {name}")
            
        elif unit in ['tsp', 'tbsp']:
            # For other volume measurements
            if unit == 'tbsp' and amount < 0.5:
                # Convert to teaspoons
                tsp = round(amount * 3, 1)
                print(f"- {tsp} tsp {name}")
            elif unit == 'tsp' and amount < 1:
                # Show as fraction
                fraction = round(amount * 4) / 4
                parts = str(fraction).split('.')
                if len(parts) > 1 and parts[1] != '0':
                    frac_map = {'25': '1/4', '5': '1/2', '75': '3/4'}
                    frac_part = frac_map.get(parts[1][:2], '')
                    if frac_part:
                        print(f"- {frac_part} tsp {name}")
                        continue
            else:
                # Show with 1 decimal place if needed
                formatted = f"{amount:.1f}".rstrip('0').rstrip('.')
                print(f"- {formatted} {unit} {name}")
                
        else:
            # For other units (g, ml, etc.)
            formatted = f"{int(amount) if amount == int(amount) else amount}"
            print(f"- {formatted} {unit} {name}")

def main():
    """Main function to run the recipe scaler CLI."""
    # Load recipes
    recipes = load_recipes()
    
    if not recipes:
        print("No recipes found. Please check your recipes.json file.")
        return
    
    print("\n=== Recipe Scaling Utility ===\n")
    
    # Display available recipes
    print("Available recipes:")
    for i, recipe in enumerate(recipes, 1):
        print(f"{i}. {recipe['name']} (Serves {recipe['servings']})")
    
    # Get recipe selection
    while True:
        try:
            choice = int(input("\nSelect a recipe (number): ")) - 1
            if 0 <= choice < len(recipes):
                selected_recipe = recipes[choice]
                break
            print("Invalid selection. Please try again.")
        except ValueError:
            print("Please enter a valid number.")
    
    # Get desired number of servings
    while True:
        try:
            new_servings = int(input(f"\nCurrent servings: {selected_recipe['servings']}\n"
                                   f"Enter new number of servings: "))
            if new_servings > 0:
                break
            print("Please enter a positive number.")
        except ValueError:
            print("Please enter a valid number.")
    
    # Scale the recipe
    scaled_recipe = scale_recipe(selected_recipe, new_servings)
    
    if scaled_recipe:
        print("\n=== Scaled Recipe ===")
        display_recipe(scaled_recipe)

if __name__ == "__main__":
    main()
