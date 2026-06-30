import json
import os
import sys
from dotenv import load_dotenv

load_dotenv()

REASONING_EFFORT_MAP = {}


def normalize_reasoning_effort(reasoning_effort):
    if not reasoning_effort:
        return None
    normalized_effort = reasoning_effort.strip().lower()
    return REASONING_EFFORT_MAP.get(normalized_effort, normalized_effort)


def load_json_mapping(env_name):
    raw_mapping = os.environ.get(env_name)
    if not raw_mapping:
        return {}
    try:
        parsed_mapping = json.loads(raw_mapping)
    except json.JSONDecodeError as exc:
        raise ValueError(f"{env_name} must be a valid JSON object") from exc
    if not isinstance(parsed_mapping, dict):
        raise ValueError(f"{env_name} must be a valid JSON object")
    return {
        str(key).strip().lower(): str(value).strip()
        for key, value in parsed_mapping.items()
        if str(key).strip() and str(value).strip()
    }


def load_reasoning_effort_mapping(env_name):
    return {
        model: normalize_reasoning_effort(reasoning_effort)
        for model, reasoning_effort in load_json_mapping(env_name).items()
    }


# Configuration
class Config:
    def __init__(self):
        self.openai_api_key = os.environ.get("OPENAI_API_KEY")
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        # Add Anthropic API key for client validation
        self.anthropic_api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not self.anthropic_api_key:
            print("Warning: ANTHROPIC_API_KEY not set. Client API key validation will be disabled.")
        
        self.openai_base_url = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
        self.azure_api_version = os.environ.get("AZURE_API_VERSION")  # For Azure OpenAI
        self.host = os.environ.get("HOST", "0.0.0.0")
        self.port = int(os.environ.get("PORT", "8082"))
        self.log_level = os.environ.get("LOG_LEVEL", "INFO")
        self.max_tokens_limit = int(os.environ.get("MAX_TOKENS_LIMIT", "4096"))
        self.min_tokens_limit = int(os.environ.get("MIN_TOKENS_LIMIT", "100"))
        self.use_responses_api = os.environ.get("USE_RESPONSES_API", "false").lower() in ("1", "true", "yes", "on")
        self.responses_streaming = os.environ.get("RESPONSES_STREAMING", "true").lower() in ("1", "true", "yes", "on")
        self.stream_accept_header = os.environ.get("STREAM_ACCEPT_HEADER", "text/event-stream")
        self.reasoning_effort = normalize_reasoning_effort(os.environ.get("REASONING_EFFORT"))
        self.reasoning_summary = os.environ.get("REASONING_SUMMARY")
        
        # Connection settings
        self.request_timeout = int(os.environ.get("REQUEST_TIMEOUT", "90"))
        self.max_retries = int(os.environ.get("MAX_RETRIES", "2"))
        self.user_agent = os.environ.get(
            "USER_AGENT",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        )
        
        # Model settings - BIG and SMALL models
        self.big_model = os.environ.get("BIG_MODEL", "gpt-4o")
        self.middle_model = os.environ.get("MIDDLE_MODEL", self.big_model)
        self.small_model = os.environ.get("SMALL_MODEL", "gpt-4o-mini")
        self.model_mapping = {
            "claude-haiku-4-5": "gpt-5.4-mini",
            "claude-opus-4-7": "gpt-5.5",
            "claude-sonnet-4-6": "gpt-5.4",
            **load_json_mapping("MODEL_MAPPING"),
        }
        self.reasoning_effort_mapping = {
            "claude-haiku-4-5": normalize_reasoning_effort("medium"),
            "claude-opus-4-7": normalize_reasoning_effort("xhigh"),
            "claude-sonnet-4-6": normalize_reasoning_effort("medium"),
            **load_reasoning_effort_mapping("REASONING_EFFORT_MAPPING"),
        }
        
    def validate_api_key(self):
        """Basic API key validation"""
        if not self.openai_api_key:
            return False
        # Basic format check for OpenAI API keys
        if not self.openai_api_key.startswith('sk-'):
            return False
        return True
        
    def validate_client_api_key(self, client_api_key):
        """Validate client's Anthropic API key"""
        # If no ANTHROPIC_API_KEY is set in environment, skip validation
        if not self.anthropic_api_key:
            return True
            
        # Check if the client's API key matches the expected value
        return client_api_key == self.anthropic_api_key
    
    def get_custom_headers(self):
        """Get custom headers from environment variables"""
        custom_headers = {}
        
        # Get all environment variables
        env_vars = dict(os.environ)
        
        # Find CUSTOM_HEADER_* environment variables
        for env_key, env_value in env_vars.items():
            if env_key.startswith('CUSTOM_HEADER_'):
                # Convert CUSTOM_HEADER_KEY to Header-Key
                # Remove 'CUSTOM_HEADER_' prefix and convert to header format
                header_name = env_key[14:]  # Remove 'CUSTOM_HEADER_' prefix
                
                if header_name:  # Make sure it's not empty
                    # Convert underscores to hyphens for HTTP header format
                    header_name = header_name.replace('_', '-')
                    custom_headers[header_name] = env_value
        
        return custom_headers

try:
    config = Config()
    print(f" Configuration loaded: API_KEY={'*' * 20}..., BASE_URL='{config.openai_base_url}'")
except Exception as e:
    print(f"=4 Configuration Error: {e}")
    sys.exit(1)
