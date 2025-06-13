from fastapi import FastAPI, UploadFile, Body, File
from pydantic import create_model
import logging
import uvicorn
from tempfile import NamedTemporaryFile, mkdtemp
from cwltool import factory
from cwltool.context import RuntimeContext
from threading import Thread
import time
from typing import Optional, List
from mcp.server.fastmcp import FastMCP
from cmdagent.tool_logic import run_tool  # <-- import shared logic
import threading

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())


class mcp_api():
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
        self.mcp = FastMCP(self.tool_name)

        @self.mcp.tool()
        async def uploadFile(file: UploadFile = File(description="The file to be uploaded to the server")) -> dict:
            """
            Upload a file to the server.

            Parameters:
                file (UploadFile): The file to be uploaded.

            Returns:
                dict: A dictionary containing the filename and filepath of the uploaded file.
            """
            with NamedTemporaryFile(delete=False) as tmp:
                contents = file.file.read()
                tmp.write(contents)
            return {"filename": file.filename, "filepath": tmp.name}

        fields_desc = ", ".join(
            f"{k}: {v.annotation.__name__ if hasattr(v.annotation, '__name__') else str(v.annotation)}"
            for k, v in self.Base.model_fields.items()
        )

        tool_desc = f"{self.tool_name}: {self.tool.t.tool.get('label', '')}\n"

        @self.mcp.tool(name=self.tool_name, description=tool_desc)
        def mcp_tool(
            data: List[self.Base] = Body(
                ...,
                description=f"Input data for '{self.tool_name}'. Fields: {fields_desc}"
            )
        ) -> dict:
            logger.info(data)
            params = data[0].model_dump()
            outs = run_tool(self.tool, params, self.outputs, self.read_outs)
            logger.info(outs)
            return outs


    def serve(self):
        print(f"Starting MCP server at http://{self.host}:{self.port}/{self.tool_name}/", flush=True)
        self.mcp.run(transport='sse')
        # thread = threading.Thread(target=self.mcp.run, kwargs={'transport': 'sse'}, daemon=True)
        # thread.start()
        # self.server_thread = thread
