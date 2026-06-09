from mcp_instance import mcp
# registers tools via @mcp.tool() decorators
import tools.read 
import tools.write
import tools.search

if __name__ == "__main__":
    mcp.run()
