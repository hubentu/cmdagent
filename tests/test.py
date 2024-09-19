from toolagent.agent import tool_agent
from toolagent.remote_api import tool_api

api = tool_api(cwl_file='tests/dockstore-tool-md5sum.cwl', tool_name='md5sum')
api.serve()

ta = tool_agent(api)
md5 = ta.create_tool()
md5(input_file="tests/dockstore-tool-md5sum.cwl")

import google.generativeai as genai
genai.configure(api_key="******")
model = genai.GenerativeModel(model_name='gemini-1.5-flash', tools=[md5])

chat = model.start_chat(enable_automatic_function_calling=True)
response = chat.send_message("what is md5 of tests/dockstore-tool-md5sum.cwl?")
response.text