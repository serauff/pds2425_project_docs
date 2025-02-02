Welcome to the pds2425 docs!
============================

Responsible for the readthedocs documentation: Seraphin Auffinger

This documentation describes the first part of the project: Generating a annotated Question and Answer Dataset

Check out the :doc:`data_generation`, :doc:`api` and :doc:`fine_tune_an` section for further information.

.. _concept
Concept
-------

This GenAI project aims to test the approach of fine-tuning models on a small, annotated Question&Answer dataset to automatically generate a larger dataset by extracting answers from the large datset with multiple models and ranking the answers by the models confidence scores. We then continue by fine-tuning models on our larger, AI-annotated dataset and evaluate the performance of different models on this dataset. This project thus acknowledges, that AI-generated annotations on the large dataset may not always be truthful.

The context of the extractive Question Answering task is the setting of a questionnaire in a business context. Thus, the real world use of the models would be to be used live, during a questionnaire. The interviewer therefore poses the question of which the answer to should be extracted from the context the interviewee is responding with. The use case further should include that the answers that can be selected in the questionnaires are structured. Along with a software, the models could then be used to automatically fill out business questionnaires live and in place.

Obvious limitations of our project are the resources to annotate a large, high quality dataset. As question-answer pairs cannot be simply annotated by using regular expressions, a human being has to read each question-answer pair and by their own judgement, select the correct response as well as document the starting index of that response in the context. Thus, we test the case of using GenAI models to automatically annotate a large dataset to be ready for fine-tuning.

Following the Dataset Generation Task, we test different models on our Dataset. However, we see that while similar architectures can extract answers from the dataset, other models are not that good. Thus, we can possibly derive that our dataset is not good for generalization.

.. _annotation results
Results of the AI-Annotation
************

On our synthetic dataframe with 2266 question answer pairs, we achieve confidence scores of, ...

... 50% and higher for 1925 Q&A-pairs,

... 75% and higher for 1521 Q&A-pairs,

... 90% and higher for 1060 Q&A-pairs,

... 95% and higher for 768 Q&A-pairs,

... 99% and higher for 411 Q&A-pairs

and a mean score of 78.21% confidence.

Of the 411 results higher than 99% we have a distribution of 108 long answers, 138 medium length answers and 165 short length answers.

Of these 411 answers, 152 times the answer type was ``"NUMBER"``, which often consisted of a number range, 147 times the answer type was ``"DATE"``, only 80 times the answer type was ``"SINGLE_SELECT"`` and only 32 times the answer was a ``"MULIT_SELECT"`` answer.

Interpretation
************

While we have a good amount of scores with acceptable confidence scores, there is a undeniable amount of 25% of our scores below 66% confidence. However, with a mean of 78.21%, good fine-tuning results may still be achievable. Further steps to take could be annotating a even larger set and filtering out Q&A-pairs that are below a reasonable confidence threshold. Further improvements on this larger dataset could then be made if a language model high in reasoning skills would reevaluate if the extracted answers can be found in the context and give suggestions. Then, to ensure a high-confidence dataset, datapoints which are deemed to be wrong Question-Answer-Pairs could again be filtered out. 

Next steps for this dataset could include, similar to the manually annotated dataset in :doc:`data_generation`, finding a way to allow for more answers to one context for validation; After one answer would be extracted by a model, another model could remove the given answer sentence from the context, store the removed sentence length and pass the context to another model for reevaluation of the presence of an answer. Then, the scores can be annotated again. This can be performed multiple times until a model denies the presence of an answer. Further, models could be used to recognize patterns of models that were used to annotate the dataset and try to change them to a pattern that is more fitting to natural language answers. E.g. some unnecessary words in a sentence that get extracted by a model with high confidence scores.

Contents
--------

.. toctree::

   usage
   api
   data_generation
   fine_tune_an
