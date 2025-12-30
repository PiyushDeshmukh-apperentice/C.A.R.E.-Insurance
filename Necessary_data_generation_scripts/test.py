# import google.generativeai as genai

# genai.configure(api_key="AIzaSyCmg7Jxh_FRSHHjp9bqTbr2PEoAW39t85U")

# models = genai.list_models()

# for m in models:
#     print(m.name, "-", m.available_methods)\

# from google.generativeai import genai

# client = genai.Client(api_key="AIzaSyCmg7Jxh_FRSHHjp9bqTbr2PEoAW39t85U")

# response = client.models.generate_content(
#     model="gemma-3-27b-it",
#     contents="Roses are red...",
# )

# print(response.text)

# curl "https://generativelanguage.googleapis.com/v1beta/models?key=AIzaSyCmg7Jxh_FRSHHjp9bqTbr2PEoAW39t85U"