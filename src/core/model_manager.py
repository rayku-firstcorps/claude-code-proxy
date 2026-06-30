from src.core.config import config

class ModelManager:
    def __init__(self, config):
        self.config = config

    def get_configured_mapping(self, claude_model: str, mapping):
        model_lower = claude_model.lower()
        for mapped_model in sorted(mapping, key=len, reverse=True):
            if model_lower == mapped_model or model_lower.startswith(f"{mapped_model}-"):
                return mapping[mapped_model]
        return None

    def map_claude_model_to_openai(self, claude_model: str) -> str:
        """Map Claude model names to OpenAI model names based on configured mappings."""
        configured_model = self.get_configured_mapping(claude_model, self.config.model_mapping)
        if configured_model:
            return configured_model

        # If it's already an OpenAI model, return as-is
        if claude_model.startswith("gpt-") or claude_model.startswith("o1-"):
            return claude_model

        # If it's other supported models (ARK/Doubao/DeepSeek), return as-is
        if (claude_model.startswith("ep-") or claude_model.startswith("doubao-") or
            claude_model.startswith("deepseek-")):
            return claude_model

        # Map based on model naming patterns
        if 'haiku' in model_lower:
            return self.config.small_model
        elif 'sonnet' in model_lower:
            return self.config.middle_model
        elif 'opus' in model_lower:
            return self.config.big_model
        else:
            # Default to big model for unknown models
            return self.config.big_model

    def get_reasoning_effort_for_model(self, claude_model: str):
        configured_effort = self.get_configured_mapping(
            claude_model,
            self.config.reasoning_effort_mapping,
        )
        return configured_effort or self.config.reasoning_effort

model_manager = ModelManager(config)