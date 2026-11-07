"""Submit the authored General; the independently trained learner remains reproducible."""
from general import Agent


def choose_action(model, observation):
    """Keep the template's model-testing interface without loading Torch during authored play."""
    from learner_agent import choose_action as learned_action
    return learned_action(model, observation)
