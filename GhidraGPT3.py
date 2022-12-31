# Ghidra GPT3 integration
# @author jumango (jumango.dev)
# @category API
# @keybinding Ctrl-Alt-G
# @menupath Tools.GhidraGPT3
# @toolbar

# config for this script
# to get api_key, access https://beta.openai.com/account/api-keys
config = {
    "api_key" : "YOUR_API_KEY_GOES_HERE",
    "prompts": [
        "explain this function",
        "decompile to python",
        "explain all variables",
        "is this vulnerable?, if so, explain or write exploit in python",
        "any unknowns in this function?",
        "next to do based on this code?",
    ],
    "add_comment": True,
    "model": "text-davinci-003",
    "max_tokens": 2048,
    "temperature": 0.9,
}

# decompiler
from ghidra.util.task import TaskMonitor
from ghidra.app.decompiler import DecompInterface
# for gpt3 api request
import urllib2
import json

def error(while_str, err_str):
    askString("error while " + while_str, "because", err_str)
    panic()

# cut string by 40 then return \r separated string
def cut_str_into_arr_str(prompt_str):
    div_by = 40
    return "\n".join([prompt_str[i:i+div_by] for i in range(0, len(prompt_str), div_by)])

# user prompt input
prompt_choice = askChoice("Prompt", "choose prompt", config["prompts"], config["prompts"][0] )

# get c file
print("decompiling...")
try:
    decObj = DecompInterface()
    decObj.openProgram(currentProgram)
    selected_fun_name = getFunctionContaining(currentLocation.getAddress())
    c_code = decObj.decompileFunction(selected_fun_name, 30, TaskMonitor.DUMMY).getDecompiledFunction().getC()
except Exception as e:
    error("decompiling", str(e))

# decompile validation
if len(c_code) == 0:
    error("decompiling", "decompiler returned empty string")

print("function " + str(selected_fun_name) + " decompiled to c.")

# request to gpt3
prompt = ""
prompt += prompt_choice + "\r\n"
prompt += c_code
dataObj = {
    "prompt": prompt,
    "model": config["model"],
    "max_tokens": config["max_tokens"],
    "temperature": config["temperature"],
}
print("request started...")

try:
    dataObj = json.dumps(dataObj)
    req = urllib2.Request('https://api.openai.com/v1/completions', dataObj, {'Authorization': 'Bearer ' + config["api_key"], 'Content-Type': 'application/json'})
    res = urllib2.urlopen(req).read()
    res_text = json.loads(res)["choices"][0]["text"]
    # print
    popup(res_text)
except Exception as e:
    error("requesting 2 gpt3", str(e))

print("done")

# add comment to the function with res_text
if config["add_comment"]:
    try:
        comment = "GPT3 answer:\r" + cut_str_into_arr_str(res_text)
        selected_fun_name.setComment(comment)
    except Exception as e:
        error("adding comment", str(e))
