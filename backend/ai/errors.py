"""Errors shared by the AI gateway and the features that call it."""


class AIUnavailable(RuntimeError):
    """No AI provider could answer (all out of credits/quota, down, or none configured)."""


class ModelNotFound(RuntimeError):
    """A model chosen in a setting (e.g. FAHIM_PAPER_MODEL) is not one the provider knows.

    A configuration mistake, not an outage: callers retry with the default model, and it never
    counts towards switching the provider off.
    """

    def __init__(self, model: str, message: str):
        super().__init__(message)
        self.model = model


class AILimitReached(RuntimeError):
    """This learner reached today's AI limit, or the monthly AI budget is spent (hard stop)."""

    def __init__(self, reason: str, message: str):
        super().__init__(message)
        self.reason = reason  # "daily" or "budget"
