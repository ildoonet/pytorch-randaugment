import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer


lang_en = "eng_Latn"
lang_kr = "kor_Hang"


class Translator:
    def __init__(self) -> None:
        # model_id = "facebook/nllb-200-3.3B"
        model_id = "facebook/nllb-200-distilled-600M"
        self.device = torch.device('cuda')
        print(model_id, '...')
        self.tokenizer = AutoTokenizer.from_pretrained(model_id)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_id)
        self.model.eval().to(self.device)

    def translate(self, article, lang_to):
        inputs = self.tokenizer(article, return_tensors="pt")
        inputs = {k:v.to(self.device) for k,v in inputs.items()}

        translated_tokens = self.model.generate(
            **inputs, forced_bos_token_id=self.tokenizer.lang_code_to_id[lang_to], max_length=200
        )

        return self.tokenizer.batch_decode(translated_tokens, skip_special_tokens=True)[0]



if __name__ == '__main__':
    t = Translator()

    article = "UN Chief says there is no military solution in Syria"
    print(t.translate(article, lang_kr))

    article = "배고파"
    print(t.translate(article, lang_en))
