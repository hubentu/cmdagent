from cmdagent.mcp_api import mcp_api

mcp = mcp_api(host='0.0.0.0', port=8000)
mcp.add_tool('tests/dockstore-tool-md5sum.cwl', 'md5sum')
mcp.add_tool('tests/dockstore-tool-md5sum.cwl', 'md5')
mcp.serve()