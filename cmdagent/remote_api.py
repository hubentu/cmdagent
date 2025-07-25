from fastapi import FastAPI, UploadFile, Body
from pydantic import create_model
import logging
import uvicorn
from tempfile import NamedTemporaryFile, mkdtemp
from cwltool import factory
from cwltool.context import RuntimeContext
from threading import Thread
import time
from typing import Optional, List
from cmdagent.tool_logic import run_tool  # <-- import shared logic


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


class tool_api():
    def __init__(self, cwl_file, tool_name='tool', host='0.0.0.0', port=8000, read_outs=True):
        """
        Initializes a tool_api object, which is used to create a FastAPI server for a given CWL file.

        Parameters:
            cwl_file (str): The path to the CWL file.
            tool_name (str): The name of the tool. Defaults to 'tool'.
            host (str): The host IP address. Defaults to '0.0.0.0'.
            port (int): The port number. Defaults to 8000.
            read_outs (bool): Whether to read the outputs. Defaults to True.

        Returns:
            None
        """
        self.cwl_file = cwl_file
        self.tool_name = tool_name
        self.host = host
        self.port = port
        self.read_outs = read_outs
        self.server = None
        self.url = None
        # cwl
        runtime_context = RuntimeContext()
        runtime_context.outdir = mkdtemp()
        fac = factory.Factory(runtime_context=runtime_context)
        self.tool = fac.make(cwl_file)

        self.inputs = self.tool.t.inputs_record_schema['fields']
        self.outputs = self.tool.t.outputs_record_schema['fields']

        # map types
        it_map = {}
        for it in self.inputs:
            if 'File' in it['type']:
                it_map[it['name']] = (str, None)
            elif 'string' in it['type']:
                it_map[it['name']] = (str, None)
            elif 'double' in it['type']:
                it_map[it['name']] = (float, None)
            else:
                it_map[it['name']] = (str, None)

            if 'null' in it['type']:
                type, v = it_map[it['name']]
                it_map[it['name']] = (Optional[type], v)
    
        self.Base = create_model('Base', **it_map)

        # define tool
        # fastapi
        self.app = FastAPI()

        @self.app.post('/uploadFile/')
        async def uploadFile(file: UploadFile):
            with NamedTemporaryFile(delete=False) as tmp:
                contents = file.file.read()
                tmp.write(contents)
            return {"filename": file.filename, "filepath": tmp.name}

        @self.app.post(f"/{self.tool_name}/")  
        def tool(data: List[self.Base] = Body(...)):
            logger.info(data)
            params = data[0].model_dump()
            outs = run_tool(self.tool, params, self.outputs, self.read_outs)
            logger.info(outs)
            return outs

    def serve(self):
        """
        Starts a FastAPI server to serve the specified tool.

        This function initializes a FastAPI server and sets up the necessary routes for the specified tool. The server listens for HTTP requests on the specified host and port.
        """
        config = uvicorn.Config(app=self.app, host=self.host, port=self.port)
        self.server = uvicorn.Server(config=config)
        thread = Thread(target=self.server.run)
        thread.start()  # non-blocking call

        while not self.server.started:
            time.sleep(0.1)
        else:
            print(f"HTTP server is now running on http://{self.host}:{self.port}")
            self.url = f"http://{self.host}:{self.port}/{self.tool_name}/"

    
    def stop(self):
        """
        Stops the server by setting the should_exit flag to True.
        """
        self.server.should_exit = True



# api = tool_api(cwl_file='test_data/dockstore-tool-md5sum.cwl')
# api.serve()
# api.stop()