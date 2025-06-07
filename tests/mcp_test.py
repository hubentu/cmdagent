from cmdagent.mcp_api import mcp_api

mcp = mcp_api(cwl_file='tests/dockstore-tool-md5sum.cwl', tool_name='md5sum')
mcp.serve()
