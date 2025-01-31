from typing import List

import numpy as np

from utils.utils import split_on_words
from utils.utils import levenshtein
from yandex.models import ResponseYaGpt


class ParserResponse:
    def __init__(self, answer_index, sources, reasoning):
        self.answer_index = answer_index
        self.sources = sources
        self.reasoning = reasoning

    def __repr__(self):
        return (
            f"ParserResponse(\n"
            f"  answer_index={self.answer_index},\n"
            f"  sources={self.sources},\n"
            f"  reasoning={self.reasoning}\n"
            f")"
        )


def get_answer(candidate_answers: List[str], evaluations: List[ResponseYaGpt]) -> ParserResponse:
    print(candidate_answers, evaluations)
    cumulative_reliability = [0] * len(candidate_answers)
    fully_reliable_indices = []
    best_match_indices = []
    for eval_idx, evaluation in enumerate(evaluations):
        split_result_words = split_on_words(evaluation.answer_without_sources)
        reliability_allocation = [0] * len(candidate_answers)
        min_distance = 9999
        for answer_idx, candidate_answer in enumerate(candidate_answers):
            words_in_answer = split_on_words(candidate_answer)
            target_answer_phrase = ' '.join(words_in_answer)
            peak_assurance = 0
            for offset in range(len(split_result_words) - len(words_in_answer) + 1):
                current_phrase = ' '.join(split_result_words[offset:offset + len(words_in_answer)])
                lev_dist = levenshtein(current_phrase, target_answer_phrase)
                min_distance = min(min_distance, lev_dist)
                assurance_score = (1 - lev_dist / max(len(current_phrase), len(target_answer_phrase)))
                peak_assurance = max(peak_assurance, assurance_score)
            adjusted_reliability = peak_assurance * (1 + evaluation.is_main)
            cumulative_reliability[answer_idx] += adjusted_reliability
            reliability_allocation[answer_idx] = peak_assurance

        best_match_indices.append(int(np.argmax(reliability_allocation)))
        if min_distance <= 1:
            fully_reliable_indices.append(eval_idx)

    if not fully_reliable_indices and len(evaluations) > 0:
        fully_reliable_indices = [0]  # itmo
    fully_reliable_sources = [evaluations[idx].sources for idx in fully_reliable_indices]
    target_sources = []
    for x in fully_reliable_sources:
        for y in x:
            target_sources.append(y)

    reasoning_resource = None
    for idx in fully_reliable_indices:
        if evaluations[idx].is_main:
            reasoning_resource = evaluations[idx]
    if reasoning_resource is None and len(fully_reliable_indices) > 0:
        reasoning_resource = fully_reliable_indices[0]

    if reasoning_resource:
        reasoning = reasoning_resource.answer
        reasoning += '. '
        for source in reasoning_resource.sources:
            reasoning += f"Источник [{source.index}] - {source.title}. "
    else:
        reasoning = 'Взято из источников'

    if len(cumulative_reliability) > 0:
        return ParserResponse(
            np.argmax(cumulative_reliability) + 1,
            list(map(lambda source: source.url, target_sources[:3])),
            reasoning.replace('**', '')
        )
    else:
        return ParserResponse(1, [], reasoning)
