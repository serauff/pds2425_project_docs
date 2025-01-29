Welcome to the pds2425 docs!
============================

We host our documentation on Read the Docs

Check out the :doc:`data_generation`, :doc:`api` and :doc:`fine_tune_an` section for further information.

Concept
-------

This GenAI project aims to test the approach of fine-tuning models on a small, annotated Question&Answer dataset to automatically generate a larger dataset by extracting answers from the large datset with multiple models and ranking the answers by the models confidence scores. We then continue by fine-tuning models on our larger, AI-annotated dataset and evaluate the performance of different models on this dataset. This project thus acknowledges, that AI-generated annotations on the large dataset may not always be truthful.

The context of the extractive Question Answering task are the setting of a questionnaire in a business context. Thus, the real world use of the models would be to be used live, during a questionnaire. The interviewer therefore poses the question of which the answer to should be extracted from the context the interviewee is responding with. The use case further should include that the answers that can be selected in the questionnaires are structured. Along with a software, the models could then be used to automatically fill out business questionnaires live and in place.

Obvious limitations of our project are the resources to annotate a large, high quality dataset. As question-answer pairs cannot be simply annotated by using regular expressions, a human being has to read each question-answer pair and by their own judgement, select the correct response as well as document the starting index of that response in the context. Thus, we test the case of using GenAI models to automatically annotate a large dataset to be ready for fine-tuning. 

.. note::

   This project is under active development.

Contents
--------

.. toctree::

   usage
   api
   data_generation
   fine_tune_an
