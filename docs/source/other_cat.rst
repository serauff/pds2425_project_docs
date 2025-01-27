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
>>>path_list = ['/content/sample_data/questionnaire1.json','/content/sample_data/questionnaire2.json','/content/sample_data/questionnaire3.json',
             '/content/sample_data/questionnaire4.json','/content/sample_data/questionnaire5.json']
>>>df = generate_data(path_list)
.. _Prompting Gemini via API:
Prompting Gemini via API
------------
.. _Generating Question Datset:
Generating Question Dataset
------------
.. _Generating QA Dataset
Generating Question Dataset
------------
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
