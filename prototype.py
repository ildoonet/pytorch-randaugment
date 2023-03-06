import openai


openai.api_key = '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'


completion = openai.ChatCompletion.create(
  model="gpt-3.5-turbo", 
  messages=[{"role": "user", "content": "Tell the world about the ChatGPT API in the style of a pirate."}]
)

print(completion)
