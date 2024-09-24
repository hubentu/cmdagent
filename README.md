# Tool Agent README
======================

## Overview

Tool Agent is a Python package that converts any command-line tool into a Large Language Model (LLM) agent. This allows you to interact with the tool using natural language, making it easier to use and integrate with other applications.

## Requirements

* Python 3.12 or later
* FastAPI
* Requests
* Pydantic
* Uvicorn
* cwltool

## Installation

To install Tool Agent, run the following command:
```bash
pip install git+https://github.com/hubentu/cmdagent
```
## Usage

### Creating an API

To create an API, import the `tool_api` function from `cmdagent.remote_api` and pass in the path to a CWL file and the name of the tool:
```python
from cmdagent.remote_api import tool_api

api = tool_api(cwl_file='tests/dockstore-tool-md5sum.cwl', tool_name='md5sum')
api.serve()
```
The `api.serve()` method will start a RESTful API as a service, allowing you to run the tool remotely from the cloud or locally.

### Creating a Tool Agent

To create a tool agent, import the `cmdagent` function from `cmdagent.agent` and pass in the API instance:
```python
from cmdagent.agent import cmdagent

ta = cmdagent(api)
md5 = ta.create_tool()
md5(input_file="tests/dockstore-tool-md5sum.cwl")
```
Function `md5` is created automatically based on the `api`.

### Integrating with Gemini

To integrate the tool agent with Gemini, import the `GenerativeModel` class from `google.generativeai` and create a new instance:
```python
import google.generativeai as genai

genai.configure(api_key="******")
model = genai.GenerativeModel(model_name='gemini-1.5-flash', tools=[md5])

chat = model.start_chat(enable_automatic_function_calling=True)
response = chat.send_message("what is md5 of tests/dockstore-tool-md5sum.cwl?")
response.text
```
```
'The md5sum of tests/dockstore-tool-md5sum.cwl is ad59d9e9ed6344f5c20ee7e0143c6c12. \n'
```
