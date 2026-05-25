from Utils.api_call import call_api

def main():
    prompt = input("Enter a prompt for the API: ")
    response = call_api(prompt)
    print(f"Response from API: {response}")

if __name__ == "__main__":
    main()