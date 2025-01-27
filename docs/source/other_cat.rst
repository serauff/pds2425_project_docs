Data Generation
====
.. _Initial Data Generation:
Initial Data Generation
------------
For the initial Data Generation as in reading our seed data, the project expects the questionnaires provided by snapADDY as a list of paths in with the questionnaire in .json format. 
To read the json files, use the ``data_gen.generate_data(path_list)`` function and pass a list of paths to the questionnaires.

.. autofunction:: data_gen.generate_data(path_list)

The ``path_list`` parameter should be a list of strings.

For example:

>>> path_list = ['/content/sample_data/questionnaire1.json','/content/sample_data/questionnaire2.json',...]
>>> generate_data(path_list)
>>> returns dataframe with ['id','option','question','type','questionnaire']

.. _Prompting Gemini via API:
Prompting Gemini via API
------------

Generate with message
************

To prompt the gemini api effectively, we construct a function to generate content in a chat window by employing the function :py:func:`data_gen.generate_with_msg`

.. autofunction:: data_gen.generate_with_msg(chat_msg,chat,tier)

The ``chat_msg`` parameter should be a string, containing the instructions for the model.
The ``chat`` parameter is a chat dictionary, containing the context in which content is to be generated.
The ``tier`` parameter is for the user to select. If the parameter is set to ``"paid"``, the function will send up to 1.500 API requests before waiting for 60 seconds.
Else, the function will halt for 60 seconds after 10 requests.

For example:

>>> import time
>>> generate_with_msg("Generate a answer to the question x", chat, "paid")
>>> tuple["Generate a answer to question x", "Answer to question x"]

Initialise the chat window
***********

To initialise the chat window the function :py:func:`data_gen.init_context` can be used. 

.. autofunction:: data_gen.init_context(context)

For example:

>>> model = genai.GenerativeModel("gemini-1.5-flash")
>>> chat = init_context("You are a helpful assistant in generating questionnaire data. Please provide answers to the following questions.")

.. _Generating Question Datset:
Generating Question Dataset
------------

To generate the questions dataset, the :py:func:`data_gen.generate_q_dataset` function can be used

.. autofunction:: data_gen.generate_q_dataset(question_row, chat)

While the basic instruction for generating the questions is hardcoded, the questions that are handed over to :py:func:`data_gen.generate_with_msg` are retrieved from the
dataframe column over the parameter ``question_row`` which can be a string such as ``questions``, is used to format the instruction string for each question that should be generated.

For example:

>>> model = genai.GenerativeModel("gemini-1.5-flash")
>>> chat = init_context("You are a helpful assistant in generating questionnaire data. Please provide answers to the following questions.")
>>> questions = generate_q_dataset('question', chat)

.. _Generating QA Dataset
Generating Question&Answer Dataset
------------

After generating full-text questions, we can use the :py:func:`data_gen.generate_answers` function for generating the full question & answer dataset. 

.. autofunction:: data_gen.generate_answers(df_qa, answer_row, question_row, type_row, chat, plan)

The ``df_qa`` parameter should be a dataframe containing a column ``answer_row`` with answers options to given questions from a ``question_row``, as well as a ``type_row`` 
which indicates different handling (such as answers with multiple answer options, single answer options or answers with special characters).
Further, the ``chat`` parameter expects a chat object that has been initialised with fitting context. The ``plan`` parameter can be used to set the generation to the "paid" tier
through the :py:func:`data_gen.generate_with_msg` function.

For example:

>>> chat = reset_context()
>>> context = "Your role is a business representative that gets interviewed and is being asked to provide information about different topics"
>>> chat = init_context(context)
>>> df_qa = generate_answers(df_wit_questions, 'column_with_answers', 'column_with_questions, 'type_column', chat)

.. _Dataset Annotation
Dataset Annotation
------------
.. _other_cat:
This is a new row in the general cats

To rank the answers by the score of the different models, you call the ``rank_answers(df: pd.DataFrame)->pd.DataFrame`` function.

.. autofunction:: rank_answers(df: pd.DataFrame)->pd.DataFrame
The ``kind`` parameter should be a ``"pandas.DataFrame``. :py:func:`rank_answers(df: pd.DataFrame)->pd.DataFrame` will rank the answers according to the best performers.

.. code-block:: console

   (.venv) $ pip install lumache

.. autosummary::
   :toctree: generated

   lumache
