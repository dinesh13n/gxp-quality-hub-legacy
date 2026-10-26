"""Stage 44 error codes for the OPTIONAL, OFF-BY-DEFAULT, advisory Azure OpenAI document Q&A (OD-40).

Two CLI exit codes in one area (AI): 40 = the hub refused (policy, configuration, retrieval, limits, grounding); 41 = the model provider failed
(timeout, rate limit, HTTP error, unusable response). Messages are fixed per code; provider text, questions and document text only ever go
into `details`, and never an API key (hub.adapters.azure_openai redacts the key before it builds any detail). Kept in hub/core so that both
hub.ai and hub/adapters/azure_openai.py can raise them without a package cycle.
"""
from hub.core.errors import HubError


class AiDisabled(HubError):
    code, exit_code, http, message = "E-AI-DISABLED", 40, 501, "the optional AI document Q&A is not enabled (ai.enabled is false)"


class AiNotConfigured(HubError):
    code, exit_code, http, message = "E-AI-NOT-CONFIGURED", 40, 501, "the AI provider settings are missing or invalid"


class AiNonSynthetic(HubError):
    code, exit_code, http, message = "E-AI-NON-SYNTHETIC", 40, 403, "refused: the data or corpus is not flagged synthetic"


class AiPrincipalRefused(HubError):
    code, exit_code, http, message = "E-AI-PRINCIPAL-REFUSED", 40, 403, "the principal is unknown, inactive or has no search role"


class AiQuestionInvalid(HubError):
    code, exit_code, http, message = "E-AI-QUESTION-INVALID", 40, 422, "the question is empty, too long or malformed"


class AiNoRetrieval(HubError):
    code, exit_code, http, message = "E-AI-NO-RETRIEVAL", 40, 404, "no usable source was retrieved; no model call was made"


class AiRateLimited(HubError):
    code, exit_code, http, message = "E-AI-RATE-LIMITED", 40, 429, "AI request rate limit reached; no model call was made"


class AiBudgetExceeded(HubError):
    code, exit_code, http, message = "E-AI-BUDGET-EXCEEDED", 40, 429, "AI usage budget would be exceeded; no model call was made"


class AiUngrounded(HubError):
    code, exit_code, http, message = "E-AI-UNGROUNDED", 40, 422, "the model answer failed the grounding / citation check and was withheld"


class AiProviderTimeout(HubError):
    code, exit_code, http, message = "E-AI-PROVIDER-TIMEOUT", 41, 504, "the model provider did not answer in time"


class AiProviderRateLimited(HubError):
    code, exit_code, http, message = "E-AI-PROVIDER-RATE-LIMITED", 41, 429, "the model provider answered 429 (rate limit)"


class AiProviderRejected(HubError):
    code, exit_code, http, message = "E-AI-PROVIDER-REJECTED", 41, 502, "the model provider refused the request (HTTP 4xx, authentication or content filter)"


class AiProviderUnavailable(HubError):
    code, exit_code, http, message = "E-AI-PROVIDER-UNAVAILABLE", 41, 502, "the model provider is unreachable or answered HTTP 5xx"


class AiProviderBadResponse(HubError):
    code, exit_code, http, message = "E-AI-PROVIDER-BAD-RESPONSE", 41, 502, "the model provider answer was not usable"
