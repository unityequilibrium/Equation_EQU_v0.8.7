# AI Training Data Sources

## Real Sources:
1. **Weights & Biases**: https://wandb.ai/
2. **Hugging Face**: https://huggingface.co/
3. **Papers With Code**: https://paperswithcode.com/

## Published References:
- GPT-2: Radford et al. 2019
- LLaMA: Touvron et al. 2023
- BERT: Devlin et al. 2018

## How to Get Real Data:
```python
import wandb
api = wandb.Api()
runs = api.runs("openai/gpt-2")
```
