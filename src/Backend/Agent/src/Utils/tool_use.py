import Tools

def tool_use(tool_name: str,*args,**kwargs):
    if tool_name in Tools.__all__:
        tool = getattr(Tools, tool_name)
        return tool.main(*args,**kwargs)