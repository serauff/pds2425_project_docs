"""
Lumache - Python library for cooks and food lovers.
"""

__version__ = "0.1.0"


class InvalidKindError(Exception):
    """Raised if the kind is invalid."""
    pass



def get_random_ingredients(kind=None):
    """
    Return a list of random ingredients as strings.

    :param kind: Optional "kind" of ingredients.
    :type kind: list[str] or None
    :raise lumache.InvalidKindError: If the kind is invalid.
    :return: The ingredients list.
    :rtype: list[str]
    """

    str = """
        wue wue weu
        """
    return ["shells", "gorgonzola", "parsley"]

def generate_data(path_list):
    """
    Generates a single pandas DataFrame by processing a list of JSON files containing questionnaire data.

    :param path_list: A list of file paths to JSON files. Each JSON file is expected to contain a structure 
                  with an 'options' key for nested data and 'question' and 'type' keys for metadata.
    :type path_list: list of str
    :return: A pandas DataFrame with the following columns:
         - Columns from the 'options' key in the JSON data.
         - 'question': The question associated with each option.
         - 'type': The type of question.
         - 'questionnaire': An identifier for the questionnaire, incremented for each JSON file in the input list.
    :rtype: pandas.DataFrame
    """
    df_list = []
    i=1
    for path in path_list:
        with open(path, 'r') as f:
            data = json.load(f)
        df = pd.json_normalize(data, record_path='options', meta=['question', 'type'])
        df['questionnaire'] = i
        i+=1
        df_list.append(df)  # Append the DataFrame to the list
    dfq1 = pd.concat(df_list, axis=0)  # Concatenate all DataFrames in the list
    return dfq1
