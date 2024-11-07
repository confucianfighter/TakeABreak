import requests

# Function to get an inspirational quote
def get_inspirational_quote():
    print("Getting inspirational quote from zenquotes.io")
    response = requests.get("https://zenquotes.io/api/random")
    if response.status_code == 200:
        quote_data = response.json()[0]
        return f'"{quote_data["q"]}"\n- {quote_data["a"]}'
    else:
        return "Keep going, you're doing great!"
