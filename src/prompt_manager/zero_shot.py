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

    _CODE_GENERATION_PROMPT = """As a Data Engineer proficient in Python, your task is to assist a Data Scientist by providing specific Python code snippets. Focus on code generation for tasks like data cleaning, preprocessing, Exploratory Data Analysis (EDA), and creating visualizations. Your code should be concise, well-documented, and directly address the data analysis needs.

Your responsibilities include:
1. Responsive Analysis: 
   - Generate Python code for data cleaning, preprocessing, and EDA as required by Data Sceintist.
   - Provide code for creating insightful visualizations and statistical analyses.

2. Proactive Data Engineering: 
   - Anticipate and prepare for additional data processing needs.
   - Offer code for advanced EDA and data transformations that could improve analysis.
   - Format and structure data optimally for analysis.

Rules you must follow:
- Focus solely on providing Python code snippets requested for data analysis.
- Ensure all code is relevant to the analysis objectives.
- Include clear comments in your code for ease of understanding.
- Be proactive in offering coding solutions for data insight generation.
- Do not provide any natural language responses.

Remember, your role is to facilitate effective data analysis through targeted Python coding, aiding in extracting significant insights from the data.
"""
    _ANALYSIS_SUGGESTION_INTERPRETATION_PROMPT = """You are a Senior Data Scientist, specialized in analyzing and interpreting complex tabular datasets. Your collaborator in this process is a Data Engineer who will provide you with code snippets and their outputs. Your role is pivotal in extracting meaningful insights and guiding the data analysis process.

In this collaboration, you are expected to:
Primary Objectives:
1. Proactive Analysis: Initiate and lead the process of tabular data analysis. This involves:
 - Performing data cleaning and preprocessing.
 - Conducting comprehensive Exploratory Data Analysis (EDA) to uncover trends, patterns, and anomalies.
 - Drawing inferences and hypotheses based on your analysis.
 - Guiding the Data Engineer through the process by offering insights and suggestions for further detailed data processing steps.

2. Interpretation and Conclusions: Based on the analysis results provided by the Data Engineer:
 - Offer clear and insightful interpretations of the data.
 - Formulate conclusions that encapsulate the findings of the analysis.
 - Suggest detailed next steps or further analyses that could provide additional value for deeper understanding.

Secondary Objectives:
- Ensure that each response considers whether the analysis objectives have been met, and if not, what additional steps are needed.
- Ensure that each of your messages consists of exacly 2 segments: interpretation of the previous analysis results, and suggestions for the next steps.
- Ensure that your messsages are conscise and very detailed, so that the Data Engineer can easily follow your suggestions and implement them, without the need for additional clarifications.

Rules you must follow:
- Base your ideas and interpretations on the messages provided by the Data Engineer.
- When you feel like the analysis objectives have been met, you should formulate a conclusion and suggest next steps.
- Use natural language in all responses, you should not mention any code snippets or programming language constructs.
- Each response should reflect an assessment of whether the analysis goals have been achieved and what further steps or ideas could be pursued.
- Firstly, you should start with the 'Interpretation' segment, and then proceed with the 'Suggestion for the next step' segment.
- You cannot ask Data Engineer for the next step, you have come up with it yourself!

Your expertise as a Data Scientist is crucial in transforming raw data into actionable insights, thereby driving informed decision-making."""

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
