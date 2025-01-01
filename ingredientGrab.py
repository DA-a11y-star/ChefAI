def extract_missing_ingredients(file_path):
    missing = []
    with open(file_path, "r") as file:
        lines = file.readlines()

        # Find the section "Ingredients Not Provided in Your List"
        for i, line in enumerate(lines):
            print(line)
            if "Ingredients Not Provided in Your List" in line:
                # Start reading the ingredients from the next line
                for j in range(i + 1, len(lines)):
                    ingredient = lines[j].strip()
                    if ingredient:  # Check if the line is not empty
                        missing.append(ingredient[2:])
                    else:
                        break  # Stop if an empty line is encountered
                break  # Exit after processing the ingredients section

    print("Missing Ingredients:", missing)
    return missing


extract_missing_ingredients("./recipe_format.txt")
