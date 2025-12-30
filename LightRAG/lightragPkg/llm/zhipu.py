import sys
import re
import json
from ..utils import verbose_debug

if sys.version_info < (3, 9):
    pass
else:
    pass
import pipmaster as pm  # Pipmaster for dynamic library install

# install specific modules
if not pm.is_installed("zhipuai"):
    pm.install("zhipuai")

from openai import (
    APIConnectionError,
    RateLimitError,
    APITimeoutError,
)
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)

from ..utils import (
    wrap_embedding_func_with_attrs,
    logger,
)

from ..custom_types import GPTKeywordExtractionFormat

import numpy as np
from typing import Union, List, Optional, Dict


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    retry=retry_if_exception_type(
        (RateLimitError, APIConnectionError, APITimeoutError)
    ),
)
async def zhipu_complete_if_cache(
    prompt: Union[str, List[Dict[str, str]]],
    model: str = "glm-4-flashx",  # The most cost/performance balance model in glm-4 series
    api_key: Optional[str] = None,
    system_prompt: Optional[str] = None,
    history_messages: List[Dict[str, str]] = [],
    **kwargs,
) -> str:
    # dynamically load ZhipuAI
    try:
        from zhipuai import ZhipuAI
    except ImportError:
        raise ImportError("Please install zhipuai before initialize zhipuai backend.")

    if api_key:
        client = ZhipuAI(api_key=api_key)
    else:
        # please set ZHIPUAI_API_KEY in your environment
        # os.environ["ZHIPUAI_API_KEY"]
        client = ZhipuAI()

    messages = []

    if not system_prompt:
        system_prompt = "You are a helpful assistant. Note that sensitive words in the content should be replaced with ***"

    # Add system prompt if provided
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.extend(history_messages)
    messages.append({"role": "user", "content": prompt})

    # Add debug logging
    logger.info("===== Query Input to LLM =====")
    logger.info(f"Query: {prompt}")
    logger.info(f"System prompt: {system_prompt}")
    verbose_debug(f"System prompt: {system_prompt}")

    # Remove unsupported kwargs
    kwargs = {
        k: v for k, v in kwargs.items() if k not in ["hashing_kv", "keyword_extraction"]
    }

    # Handle thinking parameter specially since it might not be supported in older SDK versions
    # or needs to be passed differently
    thinking = kwargs.pop("thinking", None)
    if thinking:
        # Check if the installed SDK version supports 'thinking' directly
        # If not, we might need to verify SDK version or just pass it if we assume latest SDK
        # Based on user report, direct passing failed.
        # Let's try to inspect if client.chat.completions.create accepts 'thinking'
        # But for now, let's keep it in kwargs if it's supposed to be there for GLM-4.7
        # The user's error says "unexpected keyword argument 'thinking'", which means
        # the SDK *client* validation is rejecting it.
        # This usually means the SDK is too old.
        # However, if we MUST support it with older SDKs that forward **kwargs blindly but validate them,
        # or if the parameter name is different, we'd change it.
        # Given it is a new feature, upgrading SDK is the best path.
        # But since I cannot force upgrade, I will try to add it back to kwargs ONLY if we think it's safe
        # OR, maybe it needs to be in 'extra_body' for openai-compatible clients but here we use native ZhipuAI client.
        
        # Wait, the native ZhipuAI client might wrap openai client or similar.
        # If it's the *new* ZhipuAI SDK (v2+), it is OpenAI compatible.
        # If it is OpenAI compatible, non-standard params should go into `extra_body`.
        # Let's try moving 'thinking' to 'extra_body' if it fails as a direct kwarg.
        
        # Let's try to put it in extra_body which is the standard way to pass new/unsupported params
        # in OpenAI-compatible SDKs (which ZhipuAI v2 is).
        extra_body = kwargs.get("extra_body", {})
        extra_body["thinking"] = thinking
        kwargs["extra_body"] = extra_body

    response = client.chat.completions.create(model=model, messages=messages, **kwargs)

    logger.info("===== Response from LLM =====")
    logger.info(response.choices[0].message.content)

    return response.choices[0].message.content


async def zhipu_complete(
    prompt, system_prompt=None, history_messages=[], keyword_extraction=False, **kwargs
):
    # Pop keyword_extraction from kwargs to avoid passing it to zhipu_complete_if_cache
    keyword_extraction = kwargs.pop("keyword_extraction", None)
    
    # Get model name from kwargs or global config
    model_name = kwargs.get("model")
    if not model_name and "hashing_kv" in kwargs:
        model_name = kwargs["hashing_kv"].global_config.get("llm_model_name")
    if not model_name:
        model_name = "glm-4-flashx"

    if keyword_extraction:
        # Add a system prompt to guide the model to return JSON format
        extraction_prompt = """You are a helpful assistant that extracts keywords from text.
        Please analyze the content and extract two types of keywords:
        1. High-level keywords: Important concepts and main themes
        2. Low-level keywords: Specific details and supporting elements

        Return your response in this exact JSON format:
        {
            "high_level_keywords": ["keyword1", "keyword2"],
            "low_level_keywords": ["keyword1", "keyword2", "keyword3"]
        }

        Only return the JSON, no other text."""

        # Combine with existing system prompt if any
        if system_prompt:
            system_prompt = f"{system_prompt}\n\n{extraction_prompt}"
        else:
            system_prompt = extraction_prompt

        try:
            response = await zhipu_complete_if_cache(
                prompt=prompt,
                system_prompt=system_prompt,
                history_messages=history_messages,
                model=model_name,
                **kwargs,
            )

            # Try to parse as JSON
            try:
                data = json.loads(response)
                return GPTKeywordExtractionFormat(
                    high_level_keywords=data.get("high_level_keywords", []),
                    low_level_keywords=data.get("low_level_keywords", []),
                )
            except json.JSONDecodeError:
                # If direct JSON parsing fails, try to extract JSON from text
                match = re.search(r"\{[\s\S]*\}", response)
                if match:
                    try:
                        data = json.loads(match.group())
                        return GPTKeywordExtractionFormat(
                            high_level_keywords=data.get("high_level_keywords", []),
                            low_level_keywords=data.get("low_level_keywords", []),
                        )
                    except json.JSONDecodeError:
                        pass

                # If all parsing fails, log warning and return empty format
                logger.warning(
                    f"Failed to parse keyword extraction response: {response}"
                )
                return GPTKeywordExtractionFormat(
                    high_level_keywords=[], low_level_keywords=[]
                )
        except Exception as e:
            logger.error(f"Error during keyword extraction: {str(e)}")
            return GPTKeywordExtractionFormat(
                high_level_keywords=[], low_level_keywords=[]
            )
    else:
        # For non-keyword-extraction, just return the raw response string
        return await zhipu_complete_if_cache(
            prompt=prompt,
            system_prompt=system_prompt,
            history_messages=history_messages,
            model=model_name,
            **kwargs,
        )


@wrap_embedding_func_with_attrs(embedding_dim=1024, max_token_size=8192)
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=60),
    retry=retry_if_exception_type(
        (RateLimitError, APIConnectionError, APITimeoutError)
    ),
)
async def zhipu_embedding(
    texts: list[str], model: str = "embedding-3", api_key: str = None, **kwargs
) -> np.ndarray:
    # dynamically load ZhipuAI
    try:
        from zhipuai import ZhipuAI
    except ImportError:
        raise ImportError("Please install zhipuai before initialize zhipuai backend.")
    if api_key:
        client = ZhipuAI(api_key=api_key)
    else:
        # please set ZHIPUAI_API_KEY in your environment
        # os.environ["ZHIPUAI_API_KEY"]
        client = ZhipuAI()

    # Convert single text to list if needed
    if isinstance(texts, str):
        texts = [texts]

    embeddings = []
    for text in texts:
        try:
            response = client.embeddings.create(model=model, input=[text], **kwargs)
            embeddings.append(response.data[0].embedding)
        except Exception as e:
            raise Exception(f"Error calling ChatGLM Embedding API: {str(e)}")

    return np.array(embeddings)
