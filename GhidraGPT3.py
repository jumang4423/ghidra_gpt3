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
        "is this vulnerable?, if so, explain or write exploit in python",
        "is this function safe?",
        "any questions to understand this function more?",
        "next to do based on this code?",
    ],
    "model": "text-davinci-003"
}

# decompiler
from ghidra.util.task import TaskMonitor
from ghidra.app.decompiler import DecompInterface
# for gpt3 api request
import urllib2
import json

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
    askString("error while decompiling", "because", str(e))
    panic()

print("function " + str(selected_fun_name) + " decompiled to c.")

# request to gpt3
prompt = ""
prompt += prompt_choice + "\r\n"
prompt += c_code
dataObj = {
    "prompt": prompt,
    "max_tokens": 2048,
    "model": config["model"]
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
    askString("error while asking to gpt3", "because", str(e))
    panic()

print("done")
