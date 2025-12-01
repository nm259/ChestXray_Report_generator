import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

def load_chexagent_model(model_name="StanfordAIMI/CheXagent-2-3b"):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    dtype = torch.bfloat16 if device == "cuda" else torch.float32
    
    tokenizer = AutoTokenizer.from_pretrained(
        model_name,
        trust_remote_code=True,
        revision="main"
    )
    
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        device_map="auto",
        trust_remote_code=True,
        revision="main"
    )
    model = model.to(dtype)
    model.eval()
    
    return model, tokenizer, device