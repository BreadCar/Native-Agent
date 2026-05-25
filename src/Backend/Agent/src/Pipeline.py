from Tools.api_call import call_api

def main():
    prompt = "What is the capital of France?"
    response = call_api(prompt)
    print(f"Response from API: {response}")

if __name__ == "__main__":
    main()