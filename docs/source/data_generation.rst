Data Generation
====
.. _Initial Data Generation:
Initial Data Generation
------------
For the initial Data Generation as in reading our seed data, the project expects the questionnaires provided by snapADDY as a list of paths in with the questionnaire in .json format. 
To read the json files, use the ``data_gen.generate_data(path_list)`` function and pass a list of paths to the questionnaires.

.. autofunction:: data_gen.generate_data

The ``path_list`` parameter should be a list of strings.

For example:

>>> path_list = ['/content/sample_data/questionnaire1.json','/content/sample_data/questionnaire2.json',...]
>>> df = generate_data(path_list)
>>> returns dataframe with ['id','option','question','type','questionnaire']

However, for fetching json data from alternative sources, the :py:func:`data_gen.generate_data_web` function allows for passing a list of URL's to the function. The ``path_list`` parameter can be a list of ``URL's``.

For example:

>>> path_list = []
>>> path = 'https://raw.githubusercontent.com/serauff/data/refs/heads/main/questionnaires/'
>>> for i in range(1,6):
>>>   path_list.append(path + f'questionnaire{i}.json')
>>> df = generate_data_web(path_list)
>>> returns dataframe with ['id','option','question','type','questionnaire']

.. autofunction:: data_gen.generate_data_web

.. _Prompting Gemini via API:
Prompting Gemini via API
------------

Generate with message
************

To prompt the gemini api effectively, we construct a function to generate content in a chat window by employing the function :py:func:`data_gen.generate_with_msg`

.. autofunction:: data_gen.generate_with_msg

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

.. autofunction:: data_gen.init_context

For example:

>>> model = genai.GenerativeModel("gemini-1.5-flash")
>>> chat = init_context("You are a helpful assistant in generating questionnaire data. Please provide answers to the following questions.")

Instructions for Generation
************

For adapting the outputs, a ``instructions`` template is prepared, which is derived from the different question types. For example, the function :py:func:`data_gen.generate_q_dataset` scans the ``instructions`` template for a matching instruction for generation. 

E.g.:

>>> instructions = {
>>> 'MULTI_SELECT': "To answer the questionnaire, write a natural, full text answer to the topic of {question}, with the answer options being:\n {answer}\n. Always incorporate at least one of the answers. Keep a human tone to simulate the situation of a questionnaire.",
>>> 'NUMBER': "To answer the questionnaire, write an answer to the topic of {question} including a numerical, realistic number, with the answer options being:\n {answer}\n. Always incorporate at least one of the answers. Keep a human tone to simulate the situation of a questionnaire.",
>>> 'TEXT': "The provided part of the questionnaire is about {question}, with the instruction being:\n {answer}\n. Keep a human tone to simulate the situation of a questionnaire.",
>>> 'DATE': "The provided part of the questionnaire is about {question}, with the instruction being to provide:\n {answer}\n. Incorporate a numerical value and keep a human tone to simulate the situation of a questionnaire.",
>>> 'SINGLE_SELECT': "To answer the questionnaire, write a natural, full text answer to the topic of {question}, with the answer options being:\n {answer}\n. Always incorporate at least one of the answers. Keep a human tone to simulate the situation of a questionnaire."
>>> }

During the generation stage, :py:func:`data_gen.generate_q_dataset` thus scans for a given instruction field in the ``"type"`` column of the dataframe that has been passed. With this, we can dynamically create different shapes of questionnaires. We leverage this effectively, to create ``short``, ``medium`` and ``long`` answers. The instructions field further uses an f-string to dynamically replace the ``{question}`` within the instruction strings.

Following, this means we can use the :py:func:`data_gen.init_context` function to initialise a certain wishful setting for the Large Language Model and then can use a fitting instruction field to adapt the answers. This can help in creating a diverse answer set, containing questions that can be answered with multiple options, one single option, open questions as well as number ranges or dates.

.. _Generating Question Datset:
Generating Question Dataset
------------

To generate the questions dataset, the :py:func:`data_gen.generate_q_dataset` function can be used

.. autofunction:: data_gen.generate_q_dataset

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

.. autofunction:: data_gen.generate_answers

The ``df_qa`` parameter should be a dataframe containing a column ``answer_row`` with answers options to given questions from a ``question_row``, as well as a ``type_row`` 
which indicates different handling (such as answers with multiple answer options, single answer options or answers with special characters).
Further, the ``chat`` parameter expects a chat object that has been initialised with fitting context. The ``plan`` parameter can be used to set the generation to the "paid" tier
through the :py:func:`data_gen.generate_with_msg` function.

For example:

>>> chat = reset_context()
>>> context = "Your role is a business representative that gets interviewed and is being asked to provide information about different topics"
>>> chat = init_context(context)
>>> df_qa = generate_answers(df_wit_questions, 'column_with_answers', 'column_with_questions, 'type_column', chat)

.. autofunction:: data_gen.reset_context()

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

.. autofunction:: data_gen.clean_df

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

.. autofunction:: data_gen.annotate_ds

.. autofunction:: data_gen.find_index_iter

Expand annotated answers
***********

For model fine-tuning purposes, models from huggingface.co expect the training data as ['context','question','answers'], 
with the 'answers' consisting of a SINGLE answer to a given question. Thus, we have to expand our dataframe to allow for training, as we currently have
multiple answers for a single question.

For this, the :py:func:`expand_answers` function steps into play, expecting a dataframe and a answer column in the format mentioned above.
Then, the function returns a dataframe where each row which had multiple answers for a single question gets duplicated and receives it's individual, single answer.

For example:

>>> df_expand = expand_answers(df, 'answers')

.. autofunction:: data_gen.expand_answers

We now have a dict in the 'answers' column in the format of {answers:['answer'], answer_start[int]}, ready for fine-tuning. 
Disclaimer: This format is inspired by the `SQUAD dataset <https://rajpurkar.github.io/SQuAD-explorer/>`_.

.. autosummary::
   :toctree: generated

   lumache
