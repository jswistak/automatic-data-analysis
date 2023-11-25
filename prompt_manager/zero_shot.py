from models.models import (
    ConversationRolesEnum,
    ConversationRolesInternalEnum,
    LLMType,
    Message,
)
from prompt_manager.ipromptmanager import IPromptManager


class ZeroShot(IPromptManager):
    """
    Class for a Zero Shot Prompt Manager.
    It generates specific prompts for a given Agent (Code Generation or Analysis Suggestion and Interpretation) based on the current conversation and the LLM type.
    """

    _CODE_GENERATION_PROMPT = """You are a data engineer, to help retrieve data by writing python code based on a request. In this interaction, you are providing data scientist with code snippets to analyze the dataset provided.
You have the following goals for this conversation:
 - (PRIMARY) You have to follow the data scientist's request and generate the requested Python code. Such that it will print the requested information.
 - (SECONDARY) Proactively take actions to perform tabular data analysis. You should perform data cleaning using Python programming language, conduct exploratory data analysis (EDA), and make inferences based on the analysis. You have to guide data scientist through the data processing by providing code snippets completing analysis steps, providing insights without explicit prompting.

The dataset is loaded into pandas and available under variable `df`.

Rules you must follow:
- You can only use Python programming language.
- In each response you have to consider whether you have completed the goal of the analysis or not.
- Each plot or graph you generate have to be saved to a file instead of being displayed on the screen. Do not use `plt.show()` or `display()` functions.

"""
    _ANALYSIS_SUGGESTION_INTERPRETATION_PROMPT = """You are a data scientist, your job is to analyze the dataset by coming up with the new ideas. The user a data engineer will provide you with code snippets and their output. In this interaction, you are responsible for analyzing the dataset and interpreting the results.

You have the following goals for this conversation:
    - (PRIMARY) Proactively take actions to perform tabular data analysis. You should perform data cleaning using, conduct exploratory data analysis (EDA), and make inferences based on the analysis. You have to guide data engineer through the data processing by providing insights without explicit prompting.
    - (SECONDARY) You have to follow the data engineer's request and interpret the results of the analysis. Such that it will print the requested information. If the data engineer completes the analysis, you have to come up with a conclusion based on the analysis. And the idea for the next step.
    
Rules you must follow:
 - You have to generate an idea and interpretation of the analysis based on the code snippets provided by the data engineer.
 - You can only use natural language, no code.
 - In each response you have to consider whether you have completed the goal of the analysis or not.
 
 """

    def __init__(self):
        super().__init__()

    def _generate_code_generation_prompt(
        self, conversation: list[Message], llm_type: LLMType
    ) -> list[Message]:
        """
        Generate a prompt for a code generation agent based on the current conversation.

        Parameters:
        - conversation (List[dict]): The current conversation context.
        - llm_type (LLMType): The type of Large Language Model.

        Returns:
        List[dict]: The generated conversation context. To be used as input for the LLM.
        """
        roles_dict = {
            ConversationRolesInternalEnum.ANALYSIS: ConversationRolesEnum.USER,
            ConversationRolesInternalEnum.CODE: ConversationRolesEnum.ASSISTANT,
        }
        llm_conversation = [
            Message(
                role=ConversationRolesEnum.SYSTEM, content=self._CODE_GENERATION_PROMPT
            ),
            *self._change_roles(conversation, roles_dict),
        ]

        return llm_conversation

    def _generate_analysis_suggestion_interpretation_prompt(
        self, conversation: list[Message], llm_type: LLMType
    ) -> list[Message]:
        """
        Generate a prompt for a code generation agent based on the current conversation.

        Parameters:
        - conversation (List[dict]): The current conversation context.
        - llm_type (LLMType): The type of Large Language Model.

        Returns:
        List[dict]: The generated conversation context. To be used as input for the LLM.
        """
        roles_dict = {
            ConversationRolesInternalEnum.ANALYSIS: ConversationRolesEnum.ASSISTANT,
            ConversationRolesInternalEnum.CODE: ConversationRolesEnum.USER,
        }
        llm_conversation = [
            Message(
                role=ConversationRolesEnum.SYSTEM,
                content=self._ANALYSIS_SUGGESTION_INTERPRETATION_PROMPT,
            ),
            *self._change_roles(conversation, roles_dict),
        ]

        return llm_conversation
