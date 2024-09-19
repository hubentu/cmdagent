
import requests
from types import FunctionType

class tool_agent():
    def __init__(self, api):

        # self.parameter_names = parameter_names
        self.api = api.server
        self.tool = api.tool
        self.url = api.url
        self.Base = api.Base
        self.tool_name = api.tool_name
        self.run = self._create_function()
        self.parameter_names = [it['name'] for it in api.tool.t.inputs_record_schema['fields']]

        #params = {'input_file': file_path}
    def upload_file(self, file_path):
        url_upload = f"http://{self.api.config.host}:{self.api.config.port}/uploadFile/"
        files = {'file': open(file_path, 'rb')}
        response = requests.post(url_upload, files=files)

        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Error uploading file: {response.text}")

    def pre_inputs(self, inputs, kwargs):
        params = kwargs.copy()
        for ip in inputs:
            if 'File' in ip['type']:
                # upload to server
                r_path = self.upload_file(kwargs[ip['name']])
                params[ip['name']] = 'file://' + r_path['filepath']
                
                # params[ip['name']] = {
                #     "class": "File",
                #     "location": r_path['filepath']
                # }
        return params


    def _create_function(self):
        def gen_function(**kwargs):
            # Ensure all required parameters are passed
            for param in self.parameter_names:
                if param not in kwargs:
                    raise ValueError(f"Missing required parameter: {param}")
                
            print(", ".join(f"{param}={kwargs[param]}" for param in self.parameter_names))

            inputs = self.tool.t.inputs_record_schema['fields']

            params = self.pre_inputs(inputs, kwargs)
            print(params)
            response = requests.post(self.url, json=[params])

            if response.status_code == 200:
                return response.json()
            else:
                raise Exception(f"Error uploading file: {response.text}")

        gen_function.__name__ = self.tool_name
        ann = {}
        for k, v in self.Base.model_fields.items():
            ann[k] = v.annotation
        ann['return'] = str
        gen_function.__annotations__ = ann

        return gen_function

    def create_tool(self):
        tool_name = self.tool_name
        param_names = self.parameter_names
        fun = self.run

        # Start building the function definition as a string
        function_code = "def {}({}):\n".format(tool_name, ", ".join(param_names))
        function_code += "    kwargs = {" + ", ".join([f"'{name}': {name}" for name in param_names]) + "}\n"
        function_code += f"    return {fun.__name__}(**kwargs)\n"
        # Define a local namespace to execute the function
        local_namespace = {}

        # Execute the function code in the local namespace
        exec(function_code, {}, local_namespace)
        
        generated_function = local_namespace[tool_name]

        # Use FunctionType to create the function, passing globals with the external function
        dynamic_func = FunctionType(
            generated_function.__code__, 
            {fun.__name__: fun},  # pass the predefined function to globals
            generated_function.__name__
        )

        # Return the generated function
        dynamic_func.__annotations__ = fun.__annotations__
        return dynamic_func

