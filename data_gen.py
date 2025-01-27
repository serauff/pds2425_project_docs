"""
data_gen - The module to generate data from questionnaires
"""

__version__ = "0.1.0"

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
#path_list = ['/content/sample_data/questionnaire1.json','/content/sample_data/questionnaire2.json','/content/sample_data/questionnaire3.json',
#             '/content/sample_data/questionnaire4.json','/content/sample_data/questionnaire5.json']

def rank_answers(df):
    """
    Ranks answers based on their scores for each row in a DataFrame and adds the ranked answers and scores as new columns.

    :param df: A pandas DataFrame containing columns for scores and answers. The score columns should have names containing the substring 'score_', and the answer columns should have names containing the substring 'answers_'.
    :type df: pandas.DataFrame
    :return: A modified DataFrame with two new columns:
         - 'ranked_answer': The answer corresponding to the highest score for each row.
         - 'ranked_score': The highest score for each row.
    :rtype: pandas.DataFrame
    """
    # Identify columns containing scores and answers
    score_cols = [col for col in df.columns if 'score_' in col]
    answer_cols = [col for col in df.columns if 'answers_' in col]

    ranked_answers = []
    ranked_scores = []
    for index, row in df.iterrows():
        best_score = -1  # Initialize with a value lower than any possible score
        best_answer = None
        for score_col, answer_col in zip(score_cols, answer_cols):
            score = row[score_col]
            if score:
              score_value = score['score']
              if score_value > best_score:
                  best_score = score_value
                  best_answer = row[answer_col]
        ranked_answers.append(best_answer)
        ranked_scores.append(score_value if score_value > best_score else best_score)

    df['ranked_answer'] = ranked_answers
    df['ranked_score'] = ranked_scores
    return df
