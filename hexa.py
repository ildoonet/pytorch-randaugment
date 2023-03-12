import torch
from transformers import T5ForConditionalGeneration, AutoTokenizer


class Hexa:
    def __init__(self) -> None:
        device = torch.device('cuda')
        self.device = device

        model_name_or_path = "/data/public/rw/team-lm/hexa_checkpoint/flan_t5_base_2gpu_30k_linear_zero_2_lr_1e4_deepspeed_bf16"
        # model_name_or_path = "/data/public/rw/team-lm/hexa_checkpoint/flan_t5_large_8gpu_30k_linear_zero_2_lr_5e4_deepspeed_bf16"    
        
        print(model_name_or_path, '...')
        self.tokenizer = AutoTokenizer.from_pretrained(model_name_or_path)
        self.model = T5ForConditionalGeneration.from_pretrained(model_name_or_path)
        self.model.eval().to(device)

    @torch.no_grad()
    def generate(self, input_text, task="search_query", max_length=128, num_beams=5, num_return_sequences=1):
        model, tokenizer = self.model, self.tokenizer

        assert task in ["search_query", "search_decision"]
        
        if task == "search_query":
            suffix = " __generate-query__"
        else:
            suffix = " __is-search-required__"
            
        input_text = input_text + suffix
        input_ids = tokenizer.encode(input_text)
        input_ids = [tokenizer.bos_token_id] + input_ids + [tokenizer.eos_token_id]
        input_ids = torch.LongTensor(input_ids).unsqueeze(0).to(self.device)
        bsz = input_ids.shape[0]
        generated_outputs = model.generate(
            input_ids,
            max_length = max_length,        
            num_beams = num_beams,
            do_sample = False,
            length_penalty = 0.65,
            no_repeat_ngram_size = 3,
            output_scores = True,
            return_dict_in_generate = True,
            num_return_sequences = num_return_sequences,
        )

        out = []
        for idx in range(num_return_sequences):
            sequences = generated_outputs.sequences[idx].tolist()
            generated_text = tokenizer.decode(
                sequences,
                skip_special_tokens=True,
                clean_up_tokenization_spaces=False
            )
            out.append(generated_text)
        return out


if __name__ == "__main__":
    device = torch.device('cuda')

    hexa = Hexa()
    
    # search-decision
    text = "Why the sky is blue ? I really wanna know !"
    pred = hexa.generate(text, task="search_decision")[0]
    print(pred) # '__do-search__'
    pred = hexa.generate(text, task="search_query")[0]
    print(pred)
    
    # search-decision
    text = "I am feeling good thanks"
    pred = hexa.generate(text, task="search_decision")[0]
    print(pred)  # '__do-not-search__'
    pred = hexa.generate(text, task="search_query")[0]
    print(pred)
    
    
    # search-query
    text = """What are the different types of lightbulbs?
    The most common light bulbs are incandescent, compact fluorescent (cfl), light emitting diodes (led), fluorescent, and halogen.
    Which light bulbs are the most efficient?
    """
    pred = hexa.generate(text, task="search_query")[0]
    print(pred) # 'What are the most efficient lightbulbs?'