import requests
import json

class gptSession():
    default_context = [
        {"role": "system", "content": "You are a helpful assistant."},
    ]
    def __init__(self,API_key, API_endpoint, model="gpt-4", temperature=1, max_tokens=None, max_context_len=7, debug_mode=True):
        self.API_key = API_key
        self.API_endpoint = API_endpoint
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.max_context_len = max_context_len
        self.debug_mode = debug_mode

        self.headers = {}
        self.context = gptSession.default_context


        self.set_headers()

        self.debug_text = ""


    def save_debug_as_file(self,file_name="debug.txt"):
        with open(file_name, "w") as f:
            f.write(self.debug_text)

    def set_headers(self):
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.API_key}",
        }

    def content_to_user_message(self,content):
        return {"role": "user", "content":content}


    def add_context(self,message,type):
        if len(self.context) > self.max_context_len:
            if self.context[-1]["role"] == "user" and type == "assistant": last_msg = self.context.pop(-1)
                
            self.context = gptSession.default_context
            if last_msg: self.context.append(last_msg)
        

        self.context.append(message)

    

    def send_message(self, content):
        message = self.content_to_user_message(content)
        response = self.generate_chat_completion(message)
        return response


    def generate_chat_completion(self, message):
        self.add_context(message, type="user")
        if self.debug_mode: self.debug_text += f"-> [DEBUG]_current_context:{self.context}"
        data = {
            "model": self.model,
            "messages": self.context,
            "temperature": self.temperature,
        }

        if self.max_tokens is not None:
            data["max_tokens"] = self.max_tokens

        response = requests.post(self.API_endpoint, headers=self.headers, data=json.dumps(data))
        if response.status_code == 200:
            response_msg = response.json()["choices"][0]["message"]
            self.add_context(message=response_msg, type="assistant")
            if self.debug_mode: self.debug_text += f"->[DEBUG]_output-from-api:{response.json()}" + "\n"
            return response_msg["content"]
        else:
            raise Exception(f"Error {response.status_code}: {response.text}")
