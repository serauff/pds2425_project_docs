Data Generation
====
.. _Initial Data Generation:
Initial Data Generation
------------
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
