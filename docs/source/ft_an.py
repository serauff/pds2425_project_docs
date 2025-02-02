"""
ft_an - The module for fine-tuning models on the manually annotated dataset.
"""

__version__ = "0.1.0"

def preprocess_training_examples(examples):
    """
    Direct source of this function: https://huggingface.co/learn/nlp-course/chapter7/7#fine-tuning-the-model-with-the-trainer-api
    
    Preprocesses training examples for a question-answering model by tokenizing the input and aligning answer positions.

    :param examples: A dictionary containing the following keys:
    
                         - "question": A list of questions as strings.
                         - "context": A list of corresponding context passages.
                         - "answers": A list of dictionaries where each dictionary contains:
                              - "text": A list of answer texts.
                              - "answer_start": A list of starting character indices for each answer.
    :type examples: dict
    :return: A dictionary of tokenized inputs with the following keys:
    
                 - Tokenized data (e.g., "input_ids", "attention_mask", etc.) as generated by the tokenizer.
                 - "start_positions": A list of token start indices for answers.
                 - "end_positions": A list of token end indices for answers.
    :rtype: dict
    """
  
    questions = [q.strip() for q in examples["question"]]
    inputs = tokenizer(
        questions,
        examples["context"],
        max_length=max_length,
        truncation="only_second",
        stride=stride,
        return_overflowing_tokens=True,
        return_offsets_mapping=True,
        padding="max_length",
    )

    offset_mapping = inputs.pop("offset_mapping")
    sample_map = inputs.pop("overflow_to_sample_mapping")
    answers = examples["answers"]
    start_positions = []
    end_positions = []

    for i, offset in enumerate(offset_mapping):
        sample_idx = sample_map[i]
        answer = answers[sample_idx]
        start_char = answer["answer_start"][0]
        end_char = answer["answer_start"][0] + len(answer["text"][0])
        sequence_ids = inputs.sequence_ids(i)

        # Find the start and end of the context
        idx = 0
        while sequence_ids[idx] != 1:
            idx += 1
        context_start = idx
        while sequence_ids[idx] == 1:
            idx += 1
        context_end = idx - 1

        # If the answer is not fully inside the context, label is (0, 0)
        if offset[context_start][0] > start_char or offset[context_end][1] < end_char:
            start_positions.append(0)
            end_positions.append(0)
        else:
            # Otherwise it's the start and end token positions
            idx = context_start
            while idx <= context_end and offset[idx][0] <= start_char:
                idx += 1
            start_positions.append(idx - 1)

            idx = context_end
            while idx >= context_start and offset[idx][1] >= end_char:
                idx -= 1
            end_positions.append(idx + 1)

    inputs["start_positions"] = start_positions
    inputs["end_positions"] = end_positions
    return inputs

def preprocess_validation_examples(examples):
    """
    Direct source of this function: https://huggingface.co/learn/nlp-course/chapter7/7#fine-tuning-the-model-with-the-trainer-api
    
    Preprocesses validation examples for a question-answering model by tokenizing the input and mapping offsets for evaluation.

    :param examples: A dictionary containing the following keys:
    
                         - "question": A list of questions as strings.
                         - "context": A list of corresponding context passages.
                         - "id": A list of unique identifiers for each example.
    :type examples: dict
    :return: A dictionary of tokenized inputs with the following keys:
    
                 - Tokenized data (e.g., "input_ids", "attention_mask", etc.) as generated by the tokenizer.
                 - "offset_mapping": A list of character-to-token offset mappings, with `None` for non-context tokens.
                 - "example_id": A list of unique example IDs mapped to the tokenized inputs.
    :rtype: dict
    """
  
    questions = [q.strip() for q in examples["question"]]
    inputs = tokenizer(
        questions,
        examples["context"],
        max_length=max_length,
        truncation="only_second",
        stride=stride,
        return_overflowing_tokens=True,
        return_offsets_mapping=True,
        padding="max_length",
    )

    sample_map = inputs.pop("overflow_to_sample_mapping")
    example_ids = []

    for i in range(len(inputs["input_ids"])):
        sample_idx = sample_map[i]
        example_ids.append(examples["id"][sample_idx])

        sequence_ids = inputs.sequence_ids(i)
        offset = inputs["offset_mapping"][i]
        inputs["offset_mapping"][i] = [
            o if sequence_ids[k] == 1 else None for k, o in enumerate(offset)
        ]

    inputs["example_id"] = example_ids
    return inputs

def compute_metrics(start_logits, end_logits, features, examples):
    """
    Direct source of this function: https://huggingface.co/learn/nlp-course/chapter7/7#fine-tuning-the-model-with-the-trainer-api
    
    Computes evaluation metrics for a question-answering model by comparing predicted answers with the ground truth.

    :param start_logits: A list or numpy array of start logits for each feature.
    :type start_logits: list or np.ndarray
    :param end_logits: A list or numpy array of end logits for each feature.
    :type end_logits: list or np.ndarray
    :param features: A list of tokenized input features containing:
    
                         - "example_id": The unique ID of the example associated with the feature.
                         - "offset_mapping": A list of character-to-token offset mappings.
    :type features: list of dict
    :param examples: A list of examples containing:
    
                         - "id": The unique ID of the example.
                         - "context": The context text from which answers are derived.
                         - "answers": A list of ground truth answers for the example.
    :type examples: list of dict
    :return: The evaluation metrics computed by comparing predictions against references. Typically includes metrics such as exact match (EM) and F1 score.
    :rtype: dict
    """
  
    example_to_features = collections.defaultdict(list)
    for idx, feature in enumerate(features):
        example_to_features[feature["example_id"]].append(idx)

    predicted_answers = []
    for example in tqdm(examples):
        example_id = example["id"]
        context = example["context"]
        answers = []

        # Loop through all features associated with that example
        for feature_index in example_to_features[example_id]:
            start_logit = start_logits[feature_index]
            end_logit = end_logits[feature_index]
            offsets = features[feature_index]["offset_mapping"]

            start_indexes = np.argsort(start_logit)[-1 : -n_best - 1 : -1].tolist()
            end_indexes = np.argsort(end_logit)[-1 : -n_best - 1 : -1].tolist()
            for start_index in start_indexes:
                for end_index in end_indexes:
                    # Skip answers that are not fully in the context
                    if offsets[start_index] is None or offsets[end_index] is None:
                        continue
                    # Skip answers with a length that is either < 0 or > max_answer_length
                    if (
                        end_index < start_index
                        or end_index - start_index + 1 > max_answer_length
                    ):
                        continue

                    answer = {
                        "text": context[offsets[start_index][0] : offsets[end_index][1]],
                        "logit_score": start_logit[start_index] + end_logit[end_index],
                    }
                    answers.append(answer)

        # Select the answer with the best score
        if len(answers) > 0:
            best_answer = max(answers, key=lambda x: x["logit_score"])
            predicted_answers.append(
                {"id": example_id, "prediction_text": best_answer["text"]}
            )
        else:
            predicted_answers.append({"id": example_id, "prediction_text": ""})

    theoretical_answers = [{"id": ex["id"], "answers": ex["answers"]} for ex in examples]
    return metric.compute(predictions=predicted_answers, references=theoretical_answers)

def annotator(df, model_checkpoint: str):
  """
  Annotates a DataFrame with answers and confidence scores generated by a question-answering model.

  :param df: The input DataFrame containing the following columns:
               - "context": The context text for each row.
               - "question": The question to be answered based on the context.
               
  :type df: pandas.DataFrame
  :param model_checkpoint: The model checkpoint or identifier to load the question-answering pipeline.
  :type model_checkpoint: str
  :return: A DataFrame with two new columns:
  
             - "answers_<model_checkpoint>": A list of dictionaries for each row containing:
               - 'answer': The predicted answer text.
               - 'answer_start': The starting character index of the answer in the context.
               - 'model': The model used for prediction.
             - "score_<model_checkpoint>": A list of dictionaries for each row containing:
               - 'score': The confidence score for the predicted answer.
               - 'model': The model used for prediction.
  :rtype: pandas.DataFrame
  """
    
  answers_list = []
  scores_list = []
  question_answerer = pipeline("question-answering", model=model_checkpoint)
  for index, row in df.iterrows():
      context = row['context']
      question = row['question']
      try:
        result = question_answerer(question=question, context=context)
        answers_list.append({'answer': result['answer'], 'answer_start': result['start'], 'model': model_checkpoint})
        scores_list.append({'score':result['score'], 'model':model_checkpoint})
      except Exception as e:
        print(f"Error processing row {index}: {e}")
        answers_list.append(None)
        scores_list.append(None)
  answers = "answers_" + model_checkpoint
  score = "score_" + model_checkpoint
  df[answers] = answers_list
  df[score] = scores_list
  return df

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
