"""
Lumache - Python library for cooks and food lovers.
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

def generate_q_dataset(question_row: str, chat: object) -> pandas.DataFrame:
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
        instruction_q = f"\nThe followoing is the question topic for generation: {question};To generate the question, write a natural question regarding '{question}'. \nKeep a human tone to simulate the situation of a questionnaire. Output the question as plain text.If the question already is a coherent sentence, return it with no modifications. Be extra carefulnot to alter the semantic meaning of answers in the slightest and try to keep the wording as is. Examples: Question topic: 'What kind of follow up is planned' Generated Question: 'What kind of follow up is planned?' Question topic: 'What is the size of your business unit' Generated Question: 'What is the size of your business unit?'"
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
