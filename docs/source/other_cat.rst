Data Generation
====
.. _Initial Data Generation:
Initial Data Generation
------------
For the initial Data Generation as in reading our seed data, the project expects the questionnaires provided by snapADDY as a list of paths in with the questionnaire in .json format. 
To read the json files, use the ``data_gen.generate_data(path_list)`` function and pass a list of paths to the questionnaires.

.. autofunction:: data_test.generate_data

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

.. autofunction:: data_test.init_context

For example:

>>> model = genai.GenerativeModel("gemini-1.5-flash")
>>> chat = init_context("You are a helpful assistant in generating questionnaire data. Please provide answers to the following questions.")

.. _Generating Question Datset:
Generating Question Dataset
------------

To generate the questions dataset, the :py:func:`data_gen.generate_q_dataset` function can be used



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



The ``df_qa`` parameter should be a dataframe containing a column ``answer_row`` with answers options to given questions from a ``question_row``, as well as a ``type_row`` 
which indicates different handling (such as answers with multiple answer options, single answer options or answers with special characters).
Further, the ``chat`` parameter expects a chat object that has been initialised with fitting context. The ``plan`` parameter can be used to set the generation to the "paid" tier
through the :py:func:`data_gen.generate_with_msg` function.

For example:

>>> chat = reset_context()
>>> context = "Your role is a business representative that gets interviewed and is being asked to provide information about different topics"
>>> chat = init_context(context)
>>> df_qa = generate_answers(df_wit_questions, 'column_with_answers', 'column_with_questions, 'type_column', chat)

Cleaning up the dataset
************

After generating the question & answer dataset, it is obvious that it has some range for improvement, as the chat model can return some formatting problems. In our case,
the model incorporates some suggestions in square brackets. We check this with

>>> for i in range(len(df_qa.index)):
>>>      if re.search(r"\[",df_qa['answers_ft'].iloc[i]) != None:
>>>           print(df_qa['answers_ft'].iloc[i])
>>> #prints answers with square brackets

To counteract this, we call the :py:func:`data_gen.clean_df` function. The function expects multiple parameters:
A parameter describing the dataframe to be cleaned, `df`.
Further, the column where the rows are located is expected by the `row` parameter. 
A parameter containing the `prompt`, eg. `"To clean up generated texts, please replace the text within square brackets"`.
This can be referred to as the cleanup context.
Finally, a `pattern` to look for, which sends a signal to postprocess a row.

>>> cleanup_context = "To clean up generated texts, please replace the text within square brackets"
>>> column = 'answers_ft'
>>> df_clean = clean_df(df, column, cleanup_context, r"\["



.. _Dataset Annotation
Dataset Annotation
------------

To use the Dataset for fine-tuning, we need to annotate the data. This requires a column containing a dict of {answers:['answer'], answer_start[int]}
While this inevitably means that we have to go through each row by hand to decide in which context an answer is to be deemed an answer, we can at least use a function
to only use one to two lines of code per row.

To prepare a dataset for annotating with the :py:func:`annotate_ds` function, we create two new columns, 'an_answers' for the annotated answer strings and 'special_handling' with integer lists in order to select specific occurences of a string.

>>> annotate_df['an_answers'] = ''
>>> annotate_df['special_handling'] = ''

Now, for annotating, we read each paragraph and answer and annotate selectively, for example:

>>> annotate_df.loc[5,'an_answers'] = [['R&D']]
>>> annotate_df.loc[5,'special_handling'] = [[0],[2]]

The above example annotates `'R&D'` as the answer to our question and selects the first and third occurence as the starting strings.

After doing this to our whole dataframe, we can pass it to the :py:func:`annotate_ds` function

>>> annotate_df = annotate_ds(annotate_df, 'an_answers', 'context', 'special_handling')

Keep in mind: The 'context' in a Q&A system is the paragraph from which a answer is to be extracted.



Expand annotated answers
***********

For model fine-tuning purposes, models from huggingface.co expect the training data as ['context','question','answers'], 
with the 'answers' consisting of a SINGLE answer to a given question. Thus, we have to expand our dataframe to allow for training, as we currently have
multiple answers for a single question.

For this, the py:func:`expand_answers` function steps into play, expecting a dataframe and a answer column in the format mentioned above.
Then, the function returns a dataframe where each row which had multiple answers for a single question gets duplicated and receives it's individual, single answer.

For example:

>>> df_expand = expand_answers(df, 'answers')



We now have a dict in the 'answers' column in the format of {answers:['answer'], answer_start[int]}, ready for fine-tuning. 
Disclaimer: This format is inspired by the SQUAD dataset.

.. _other_cat:
This is a new row in the general cats

To rank the answers by the score of the different models, you call the ``rank_answers(df: pd.DataFrame)->pd.DataFrame`` function.


The ``kind`` parameter should be a ``"pandas.DataFrame``. :py:func:`rank_answers(df: pd.DataFrame)->pd.DataFrame` will rank the answers according to the best performers.

.. code-block:: console

   (.venv) $ pip install lumache

.. autosummary::
   :toctree: generated

   lumache
