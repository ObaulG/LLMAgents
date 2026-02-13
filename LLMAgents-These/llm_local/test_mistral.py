from vllm import LLM
from vllm.sampling_params import SamplingParams


if __name__ == "__main__":
    sampling_params = SamplingParams()
    model_name = "mistralai/Ministral-3-3B-Base-2512"
    sampling_params = SamplingParams(max_tokens=8192)
    llm = LLM(
        model=model_name,
        tokenizer_mode="mistral",
        load_format="mistral",
        config_format="mistral",
        tensor_parallel_size=1,
        quantization="awq"
    )
    messages = [
        {
            "role": "user",
            "content": "Who is the best French painter? Answer with detailed explanations.",
        }
    ]
    res = llm.chat(messages=messages, sampling_params=sampling_params)
    print(res[0].outputs[0].text)
