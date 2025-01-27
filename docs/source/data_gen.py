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
