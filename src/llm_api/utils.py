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
        stop=["</s>", "[/INST]"],
    )
    return output


def get_together_text(output: dict) -> str:
    print(output)
    return output["output"]["choices"][0]["text"]


def conversation_prompt_to_instruct(conversation: list) -> str:
    prompt = ""
    for number in range(len(conversation)):
        print(conversation[number])
        if conversation[number].role == "system":
            prompt += "<<SYS>>" + conversation[number].content + "<</SYS>>\n"
        elif conversation[number].role == "user":
            prompt += "[USER]" + conversation[number].content + "[/USER]\n"
        elif conversation[number].role == "assistant":
            prompt += "[ASSIST]" + conversation[number].content + "[/ASSIST]\n"
        else:
            raise ValueError("Invalid message role")

        print(prompt)
    return f"<s>[INST] {prompt} [/INST]"
