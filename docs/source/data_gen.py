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

def generate_data_web(path_list):
    """
    Generates a single pandas DataFrame by processing a list of JSON files containing questionnaire data.

    :param path_list: A list of file paths to JSON files, which can be stored online. Each JSON file is expected to contain a structure 
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
    i = 1
    for path in path_list:
        # Use requests to fetch data from URL
        response = requests.get(path)
        response.raise_for_status()  # Raise an exception for bad responses
        data = response.json()  
        
        df = pd.json_normalize(data, record_path='options', meta=['question', 'type'])
        df['questionnaire'] = i
        i += 1
        df_list.append(df)  
    dfq1 = pd.concat(df_list, axis=0)  
    return dfq1

def init_context(context: str) -> object:
    """
    Initialises a new chat window with the desired context.
    
    :param context: the context the chat history should be filled with.
    :type context: str
    :return: A chat object from the chat interface
    :rtype: object
    """
    chat = model.start_chat(
      history=[
        {"role": "user", "parts": f"{context}"} #the chat history is filled with a user msg.
      ]
     )
    return chat

def reset_context()->object:
    """
    Simply resets the context of the previous chat by calling a new, clear chat.

    :return: A chat object from the chat interface
    :rtype: object
    """
    chat = model.start_chat()
    return chat

def generate_q_dataset(question_row: str, chat: object)->object:
    """
    Generates a question-answer dataset by processing a DataFrame and generating natural language questions for each row.

    :param question_row: The name of the column in the DataFrame that contains question topics.
    :type question_row: str
    :param chat: An object representing the chat interface. It must have a `send_message` method to generate questions based on provided topics.
    :type chat: object
    :return: A pandas DataFrame with the following modifications:
                 - A new column, 'question_ft', containing the generated or processed questions for each row.
                 - A new column, 'prompts_q', containing the instruction prompts used for generating the questions.
    :rtype: pandas.DataFrame
    """
    df_qa = generate_data(path_list)
    df_qa.reset_index(drop=True, inplace=True) #drop the index of the questionnaires
    max_len = len(df_qa.index)
    i = 0
    while i < max_len:
        question = df_qa[question_row].iloc[i]
        instruction_q = f"""\nThe followoing is the question topic for generation: {question};
        To generate the question, write a natural question regarding '{question}'. \n
        Keep a human tone to simulate the situation of a questionnaire. Output the question as plain text.
        If the question already is a coherent sentence, return it with no modifications. Be extra careful
        not to alter the semantic meaning of answers in the slightest and try to keep the wording as is.
        Examples: Question topic: 'What kind of follow up is planned' Generated Question: 'What kind of follow up is planned?'
        Question topic: 'What is the size of your business unit' Generated Question: 'What is the size of your business unit?'"""
        question_str, response = generate_with_msg(f"{instruction_q.format(question=question)}", chat) #generate response
        while i + 1 < len(df_qa.index) and df_qa[question_row].iloc[i+1]==df_qa[question_row].iloc[i]: #only generate a single question for multiple options
          df_qa.loc[i, 'question_ft'] = response
          df_qa.loc[i, 'prompts_q'] = question_str
          i+=1
        df_qa.loc[i, 'prompts_q'] = question_str
        df_qa.loc[i, 'question_ft'] = response
        print(response)
        i+=1
    return df_qa

def generate_answers(df_qa: object, answer_row: str, question_row: str, type_row: str, chat: object, plan: str)->object:
    """
    Generates refined answers for a question-answer DataFrame by processing each row and interacting with a chat interface.

    :param df_qa: The input DataFrame containing question-answer data to be processed.
    :type df_qa: pandas.DataFrame
    :param answer_row: The name of the column in the DataFrame that contains answers.
    :type answer_row: str
    :param question_row: The name of the column in the DataFrame that contains questions.
    :type question_row: str
    :param type_row: The name of the column in the DataFrame that specifies the type of question (e.g., MULTI_SELECT).
    :type type_row: str
    :param chat: An object representing the chat interface. It must have a `send_message` method to generate responses based on prompts.
    :type chat: object
    :param plan: The subscription plan of the user, used to determine rate-limiting logic when interacting with the chat interface.
    :type plan: str
    :return: A pandas DataFrame with the following new columns:
                 - 'prompts_a': The instruction prompts used to generate refined answers.
                 - 'answers_ft': The refined answers generated for each row.
                 - 'option': The concatenated or individual answer(s) processed from the input DataFrame.
    :rtype: pandas.DataFrame
    """
    max_len = len(df_qa.index)
    i = 0
    while i < max_len:
        question = df_qa[question_row].iloc[i]
        answer = df_qa[answer_row].iloc[i]
        if df_qa[type_row].iloc[i] == 'MULTI_SELECT':
          question = df_qa[question_row].iloc[i]
          j = i #temp storage for i
          while j + 1 < len(df_qa.index) and df_qa[question_row].iloc[j] == df_qa[question_row].iloc[j + 1]:
            answer += ', ' + df_qa[answer_row].iloc[j + 1]
            j += 1
        else:
          question = df_qa[question_row].iloc[i]
          answer = df_qa[answer_row].iloc[i]
        instruction_a = instructions.get(df_qa['type'].iloc[i]) #get corresponding instruction field
        question_str, response = generate_with_msg(f"{instruction_a.format(question=question, answer=answer)}", chat, plan) #generate response
        df_qa.loc[i, 'prompts_a'] = question_str
        df_qa.loc[i, 'answers_ft'] = response
        df_qa.loc[i, 'option'] = answer
        i+=1
        if i%10 == 0:
          print("iteration ", i)
    return df_qa

def generate_with_msg(chat_msg: str, chat: object, tier: str) -> tuple[str, str]:
    """
    Generates a response to a given chat message, enforcing rate limits based on the user's subscription tier.

    :param chat_msg: The message to be sent to the chat interface.
    :type chat_msg: str
    :param chat: An object representing the chat interface. It must have a `send_message` method that accepts a string input and returns a response iterable.
    :type chat: object
    :param tier: The subscription tier of the user. Accepted values are 'paid' or any other tier indicating a free account.
    :type tier: str
    :return: A tuple containing:
                 - The original chat message (`chat_msg`).
                 - The response text from the chat interface.
    :rtype: tuple[str, str]
    """
    global req_count
    req_count += 1
    if(tier == 'paid'):
      if req_count >= 1500: #max requests per minute are 15, we use 10 to leave some headspace
        print("Waiting for 60 seconds...")
        time.sleep(60)
        req_count = 0
    else:
      if req_count >= 10: #max requests per minute are 15, we use 10 to leave some headspace
        print("Waiting for 60 seconds...")
        time.sleep(60)
        req_count = 0
    chat_rsp = chat.send_message(f"{chat_msg}")
    for chunk in chat_rsp:
        response = chunk.text
    return chat_msg, response

def clean_df(df: object, row: str, prompt: str, pattern: str)->object:
    """
    Cleans up specific rows in a DataFrame based on a given pattern by interacting with a chat interface for refinement.

    :param df: The DataFrame to be processed.
    :type df: pandas.DataFrame
    :param row: The name of the column in the DataFrame to be cleaned.
    :type row: str
    :param prompt: The initial prompt to initialize the chat interface for context setting.
    :type prompt: str
    :param pattern: A regular expression pattern used to identify rows in the specified column that require cleaning.
    :type pattern: str
    :return: A pandas DataFrame with the following modifications:
                 - The specified column (`row`) updated with cleaned text for rows matching the pattern.
                 - A new column, 'prompt_cu', containing the prompts used for cleaning each row.
    :rtype: pandas.DataFrame
    """
    chat = reset_context()
    chat = init_context(prompt)
    for i in range(len(df.index)):
     if re.search(pattern,df[row].iloc[i]) == None:
       continue
     cleanup = df[row].iloc[i]
     prompt, cleanup = generate_with_msg(cleanup, chat,'paid')
     df.loc[i, row] = cleanup
     df.loc[i, 'prompt_cu'] = prompt
    return df

def find_index_iter(answer: str, text: str)->list:
    """
    Finds all starting indices of occurrences of a given answer string within a larger text.
    
    :param answer: The substring to search for within the text.
    :type answer: str
    :param text: The larger text in which to search for the occurrences of the answer string.
    :type text: str
    :return: A list of starting indices where the answer string is found within the text.
    :rtype: list
    """
    answer = re.escape(answer)
    matches = re.finditer(answer, text)
    start_indices = [match.start() for match in matches]
    return start_indices

def annotate_ds(df: object, answer_row: str, context_row: str, special_handling_row: str)->object:
    """
    Annotates a DataFrame with answer texts and their corresponding start indices within a given context.
    
    :param df: The input DataFrame containing rows to annotate.
    :type df: pandas.DataFrame
    :param answer_row: The name of the column in the DataFrame containing a list of answers for each row.
    :type answer_row: str
    :param context_row: The name of the column in the DataFrame containing the context (text) in which to search for answers.
    :type context_row: str
    :param special_handling_row: The name of the column in the DataFrame specifying special handling instructions (e.g., specific indices to use).
    :type special_handling_row: str
    :return: A pandas DataFrame with a new column `answers`, where each row contains a list of dictionaries with:
                 - 'text': A list of answer texts found in the context.
                 - 'answer_start': A list of starting indices for each answer in the context.
    :rtype: pandas.DataFrame
    """
    df['answers'] = ''
    answer_start = []
    text = []
    for i in range(len(df.index)):
        answer_list = df[answer_row].iloc[i]
        context = df[context_row].iloc[i]
        for answer in answer_list:
              indices = find_index_iter(answer, context)
              if len(df['special_handling'].iloc[i])>0:
                text.append(answer)
                for num in df['special_handling'].iloc[i]:
                  answer_start.append(indices[num])
              else:
                for index in indices:
                  text.append(answer)
                  answer_start.append(index)
        df.loc[i, 'answers'] = [{'text': text, 'answer_start': answer_start}]
        answer_start = []
        text = []
    return df

def expand_answers(df, answer_col):
    """
    Expands rows of a DataFrame where the answer column contains a stringified list of dictionaries.
    Converts the string into a list, then expands the dictionary within it.
    
    
    :param df: A dataframe containing annotated rows with multiple answers for postprocessing
    :type df: pandas.DataFrame
    :param answer_col: the column name containing the answer data
    :type answer_col: str
    :return: Expanded dataframe, each row has only one single individual answer to a given question
    :rtype: pandas.DataFrame
    """
    expanded_rows = []

    for _, row in df.iterrows():
        # Parse the string into a list
        answers = ast.literal_eval(row[answer_col])  # Convert string to list of dictionaries

        # Extract the dictionary from the list
        answer_dict = answers[0]  # Since the list contains one dictionary

        # Expand each answer
        for text, start in zip(answer_dict['text'], answer_dict['answer_start']):
            new_row = row.copy()
            new_row[answer_col] = {"text": [text], "answer_start": [start]}
            expanded_rows.append(new_row)

    return object(expanded_rows)


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

