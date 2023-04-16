from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate

from jinja2 import Template
import json
import functools
import os

print("key:", os.environ["OPENAI_API_KEY"])

class PromptManager():
  """
    - user comes in and says "draw me a cat"
    - send this to get_rendered_prompt(instruction)
    - this should take an item or list of items from the instruction
      - give the llm a list of all items and ask it to either pick the object being modified or make a new one if its not there
      - fetch svg from gpt for each
      - put each item name into the kv store
    - create a rendered SVG from all items in the store
    - return the rendered svg
      
    
    
    
  
  """
  def __init__(self):
    
    self.llm = OpenAI(temperature=0.9, model_name="gpt-4")
    
    self.img_objects = []
    #   {"name": "green square", "svg":  "<svg></svg>"},
    #   {"name": "orange cat wearing a beret", "svg" : "<svg></svg>"},
    #  {"name": "romantic hazy filter", "svg" : "<svg></svg>"}
    # ]

    # self.img_objects_list = self.transform_img_objs(self.img_objects)
    
    self.prompt_template = """
      you are an art model ai. you control a canvas of 1000 by 1000 pixels. this canvas consists of a list of SVG objects on a canvas. users will ask you to update this canvas with different objects.  it is possible there are no elements in the canvas. do not make up any elements unless this list contains elements. if there are no elements in the canvas and there are no instructions, do not output anything. remove all whitespace from the output if you do have one.
      
      Here are the items currently in this canvas. each item is on a new line.
      
      {{ img_objects }}

      {% if instruction %}
      you have also been given an instruction:

      {{instruction}}

      analyze this instruction and please add to or modify the overall canvas image to make it reflect what the user wants.

      - if it is an instruction to add a new item, give this item a name, and return the name of the item followed by the SVG for that item, placed as described in the command. do this in the following format [item:::svg,]
      
      - if it is an instruction to modify one or more items, figure out which of the items in the canvas is being modified. output the list of items being modified. do this in the following format [item1:::svg,item2:::svg,item3:::svg]. 
      
      when creating the results output, make sure to check that each of the results are in a valid format. if one of the results seems wrong, then do not add it.
      
      {% endif %}
      """

  def transform_img_objs(self, img_objects):
      a = []
      for i in img_objects:
        a.append(f"{i['name']}: {i['svg']}")
      return "\n".join(a)
    
  def get_rendered_prompt(self, instruction=None):
    print("instruction:", instruction)
    t = Template(self.prompt_template)
    data = {
      "img_objects" : self.img_objects,
      "instruction": instruction
    }
    res = t.render(data)
    return res
  
  def run_prompt_with_state(self, instruction):
    prompt = self.get_rendered_prompt(instruction)
    print("++ \nprompt", prompt)
    prompt_result = self.llm(prompt)
    print("++\n prompt result", prompt_result)
    parsed_items = self.parse_generated_prompt_result(prompt_result)
    print("++\n prompt parsed", parsed_items)
    for p in parsed_items:
      self.img_objects.append(p)
    print("++ \nimage objects: ", self.img_objects)
    
  def parse_generated_prompt_result(self, prompt_result):
    parsed = prompt_result.split(",")
    print("1:", parsed)
    res = []
    for p in parsed:
      if len(p) > 0:
        try:
          i = p.split(":::")
          res.append({"name": i[0], "svg": i[1]})
        except(e):
          print("somethign went wrong in parsing this object")
          print(e)
        
    print("\n++ parsed: ", parsed)
    print(res)
    return res
    
    
  # def test_llm(self):
  #   text = "What would be a good company name for a company that makes colorful socks?"
  #   print(self.llm(text))
    
    
  # def get_image_obj_from_gpt(self, instruction):
  #   prompt = """for the following prompt, give the object being created a unique two word name from the instruction, create some svg code to render it, and return it in the following format. [name:::svg output]. the name should contain no other characters or whitespace than whats needed. remove all other text from the output.
    
  #   """ + instruction
  #   print(prompt)
  #   res = self.llm(prompt)
  #   print(f"[{res}]")
  #   return res
    
  # def mutate_prompt_state(self, utterance):
  #   imgobj = self.get_image_obj_from_gpt(utterance)
  #   name,svg = imgobj.split(":::")
  #   self.img_objects.append({'name' : name, 'svg': svg})
  #   self.get_svg_from_state()

  # def get_svg_from_state(self):
  #   # send the current prompt to gpt4 and get the svg back
  #   # this is raw svg that will be rendered somewhere
  #   p = self.get_rendered_prompt()  
    
 
 
instructions = [
  "draw me a green square on the right side",
  "add a blue rectangle on the top right",
  "create an orange star center bottom, to the right of the green square"
]

# r = PromptManager()
# # print(r.get_prompt(instructions))
# # print(r.get_image_obj_from_gpt(instructions[0]))
# for i in instructions:
#   print(r.run_prompt_with_state(i))
