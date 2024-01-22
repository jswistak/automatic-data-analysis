import together


def generate_together_completion(
    prompt: str,
    model: str,
    max_tokens: int = 4000,
    temperature: float = 0.7,
    top_k: int = 50,
    top_p: float = 0.7,
) -> dict:
    output = together.Complete.create(
        prompt=prompt,
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
        top_k=top_k,
        top_p=top_p,
        repetition_penalty=1.1,
        stop=["</s>", "[/INST]", "[/USER]", "[INST]", "[USER]"],
    )
    return output


def get_together_text(output: dict) -> str:
    try:
        return output["output"]["choices"][0]["text"]
    except KeyError:
        print(output)
        raise ValueError("Invalid response or text not found")


def conversation_prompt_to_instruct(conversation: list) -> str:
    prompt = ""
    for number in range(len(conversation)):
        if conversation[number].role == "system":
            prompt += "<<SYS>>" + conversation[number].content + "<</SYS>>\n"
        elif conversation[number].role == "user":
            prompt += "[USER]" + conversation[number].content + "[/USER]\n"
        elif conversation[number].role == "assistant":
            prompt += "[ASSIST]" + conversation[number].content + "[/ASSIST]\n"
        else:
            raise ValueError("Invalid message role")

    return f"<s>[INST] {prompt} [/INST]"
