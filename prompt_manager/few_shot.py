from models.models import (
    Message,
    ConversationRolesEnum,
    ConversationRolesInternalEnum,
    LLMType,
)
from prompt_manager.ipromptmanager import IPromptManager


class FewShot(IPromptManager):
    """
    Class for a Few Shot Prompt Manager.
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

Here are some examples of how you can generate code snippets:
[EXAMPLES]
Question: User Request for Feature Selection in a Dataframe
Thought: First, I need to identify the columns to be excluded from feature selection and define the function for feature selection using ANOVA.
Action:
```python
# Define the columns you want to exclude from feature selection
features_to_exclude = ['area_mean', 'perimeter_mean', 'area_worst', 'perimeter_worst', 'perimeter_se', 'area_se']

def perform_feature_selection(data: pd.DataFrame, features_to_exclude: list, target: str):
    for feature in features_to_exclude:
        SSB, SSW = 0, 0
        mean = data[feature].mean()
        for label in data[target].unique():
            temp = data[data[target] == label][feature]
            SSB += temp.shape[0] * (mean - temp.mean())**2
            SSW += np.sum((temp - temp.mean())**2)
        df_between = data[target].nunique() - 1
        df_within = data[feature].shape[0] - data[target].nunique()
        critical_value = (SSB / df_between) / (SSW / df_within)
        if critical_value < f.ppf(0.95, df_between, df_within):
            print("Failed to reject null hypothesis between", feature, 'and', target)

perform_feature_selection(data, data.columns.drop(features_to_exclude).drop('diagnosis'), 'diagnosis')
```
[END OF EXAMPLES]"""

    _ANALYSIS_SUGGESTION_INTERPRETATION_PROMPT = """You are a data scientist, your job is to analyze the dataset by coming up with the new ideas. The user a data engineer will provide you with code snippets and their output. In this interaction, you are responsible for analyzing the dataset and interpreting the results.

You have the following goals for this conversation:
    - (PRIMARY) Proactively take actions to perform tabular data analysis. You should perform data cleaning using, conduct exploratory data analysis (EDA), and make inferences based on the analysis. You have to guide data engineer through the data processing by providing insights without explicit prompting.
    - (SECONDARY) You have to follow the data engineer's request and interpret the results of the analysis. Such that it will print the requested information. If the data engineer completes the analysis, you have to come up with a conclusion based on the analysis. And the idea for the next step.
    
Rules you must follow:
 - You have to generate an idea and interpretation of the analysis based on the code snippets provided by the data engineer.
 - You can only use natural language, no code.
 - In each response you have to consider whether you have completed the goal of the analysis or not.
 
Here are some examples of how you can generate responses:
[EXAMPLES]
```request_to_data_engineer
Idea: I want to know the distribution of the data in the dataset.
```
[END OF EXAMPLES]"""

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
