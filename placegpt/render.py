from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate

from jinja2 import Template
import json
import functools
import os

print("key:", os.environ["OPENAI_API_KEY"])

class PromptManager():
  """
    - get_svg_from_state(instruction)
    * Take the current state
    * render a prompt using it
    * send this prompt to gpt4 to get the svg
    * return svg
    
    
    
  
  """
  def __init__(self):
    
    self.llm = OpenAI(temperature=0.9, model_name="gpt-4")
    self.store = {}
    
    self.img_objects = []
    #   {"name": "green square", "svg":  "<svg></svg>"},
    #   {"name": "orange cat wearing a beret", "svg" : "<svg></svg>"},
    #  {"name": "romantic hazy filter", "svg" : "<svg></svg>"}
    # ]

    self.img_objects_list = self.transform_img_objs(self.img_objects)
    
    self.prompt_template = """
      you are an art model ai. you control a canvas of 1000 by 1000 pixels. this canvas consists of a list of objects on a canvas. each has a name and an SVG definition. users will ask you to update this canvas with different objects. Here are the items currently in this canvas. generate code that will render all the following objects on this canvas.

      {{ img_objects_list }}

      {% if self.instruction %}
      you have been given an instruction:

      {{instruction}}

      from instruction please add to or modify this image.

      - if it is an instruction to add an item, return the name of the item followed by the SVG for that item, placed as described in the command.
      - if it is an instruction to modify one or more items, output the list of items being modified, and a new list of all modified items with the appropriate modifications.
      {% endif %}
      """

  def transform_img_objs(self, img_objects):
      a = []
      for i in img_objects:
        a.append(f"{i['name']}: {i['svg']}")
      return "\n".join(a)
    
  def get_rendered_prompt(self, instruction=None):
    t = Template(self.prompt_template)
    data = {
      "img_objects_list" : self.img_objects_list,
      "instruction": instruction
    }
    res = t.render(data)
    return res
  
  def test_llm(self):
    text = "What would be a good company name for a company that makes colorful socks?"
    print(self.llm(text))
    
    
  def get_image_obj_from_gpt(self, instruction):
    prompt = """for the following prompt, give the object being created a unique two word name from the instruction, create some svg code to render it, and return it in the following format. [name:::svg output]. the name should contain no other characters or whitespace than whats needed. remove all other text from the output.
    
    """ + instruction
    print(prompt)
    res = self.llm(prompt)
    print(f"[{res}]")
    return res
    
  def mutate_prompt_state(self, utterance):
    imgobj = self.get_image_obj_from_gpt(utterance)
    name,svg = imgobj.split(":::")
    self.img_objects.append({'name' : name, 'svg': svg})
    self.get_svg_from_state()

  def get_svg_from_state(self):
    # send the current prompt to gpt4 and get the svg back
    # this is raw svg that will be rendered somewhere
    p = self.get_rendered_prompt()  
    
 def get_init_prompt(self, username):
    # TODO: use username later on for some personalization?
    self.get_prompt()
 
 
instructions = [
  "draw me a green square on the right side"
]

r = PromptManager()
# print(r.get_prompt(instructions))
# print(r.get_image_obj_from_gpt(instructions[0]))
print(r.mutate_prompt_state(instructions[0]))