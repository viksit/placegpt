# %%
import functools
import json
import os
from collections import defaultdict

import openai
from jinja2 import Template
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from openai import ChatCompletion

print("key:", os.environ["OPENAI_API_KEY"])


class PromptManager:
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
        self.img_objects = defaultdict()
        #   {"name": "green square", "svg":  "<svg></svg>"},
        #   {"name": "orange cat wearing a beret", "svg" : "<svg></svg>"},
        #  {"name": "romantic hazy filter", "svg" : "<svg></svg>"}
        # ]

        # self.img_objects_list = self.transform_img_objs(self.img_objects)

        self.style_prompt = None

        self.init_messages = [
            {
                "role": "system",
                "content": """You are FiGPT. You control a canvas of 1000 by 1000 pixels. The canvas is represented as a list of SVG objects on a HTML canvas. users will ask you to update this canvas with different objects. All of these objects follow an absolute coordinate system. Please obey that when adding or modifying objects. It is possible there are no elements in the canvas. Do not make up any elements unless this list contains elements. If there are no elements in the canvas and there are no instructions, do not output anything. Remove all whitespace from the output if you do have one.""",
            },
            {
                "role": "assistant",
                "content": """Here are the items currently in this canvas. Each item is on a new line.""",
            },
            {
                "role": "assistant",
                "content": """{{ img_objects }}""",
            },
            {
                "role": "assistant",
                "content": """Please provide an instruction to add to or modify the canvas.""",
            },
        ]

        self.classify_instruction_prompt = {
            "role": "system",
            "content": "Analyze the instruction above carefully. If it is an instruction to draw, add, or modify an item, please output 'NOSTYLE' without quotes. However, if the instruction references a 'style', 'stylization', 'in the style of', etc. return the desired user style as a descriptive phrase to be passed on to a genertive AI image model like DALL-E or Stable Diffusion. **Important**: if this instruction does NOT reference style, then do NOT output the string 'NOSTYLE' without quotes - do not output anything else.",
        }

        self.get_name_prompt = {
            "role": "system",
            "content": "Analyze the instruction above carefully. If it is an instruction to add/draw/create a new item, give this item a name that is descriptive of what it is and where it is, and return the name of the item. Else, if it is an instruction to modify one or more items, first figure out which of the items in the canvas is being modified. To do this, figure out which of the names in the list above it is closest to, then return that name. **Important**: please return only a single name. Do not add any other text to the output. Remove all whitespace from the output if you do have one.",
        }

        self.add_svg_prompt = {
            "role": "system",
            "content": "Analyze the above instruction again. Write the SVG code to draw the object. **Important**: please return only valid SVG. Do not add any other text to the output. If one of the results seems wrong, then do not add it. when creating the results output, make sure to check that each of the results are in a valid SVG format. if one of the results seems wrong, then do not add it.",
        }

        self.modify_svg_prompt = {
            "role": "system",
            "content": "Analyze the above instruction again, along with the above SVG object above carefully. Write the SVG code that modifies the object precisely following the user's intruction. **Important**: please return only valid SVG. Do not add any other text to the output. If one of the results seems wrong, then do not add it. when creating the results output, make sure to check that each of the results are in a valid SVG format. if one of the results seems wrong, then do not add it.",
        }

        """
        - If it is an instruction to add a new item, give this item a name that is descriptive of what it is and where it is, and return the name of the item followed by the SVG for that item, placed as described in the command. do this in the following format [item:::svg,]
      
        - if it is an instruction to modify one or more items, first figure out which of the items in the canvas is being modified. to do this, figure out which of the names in the list above it is closest to. then, write svg code for this operation.  output the list of items being modified. do this in the following format [item1:::svg,item2:::svg,item3:::svg]. 
        
        when creating the results output, make sure to check that each of the results are in a valid format. if one of the results seems wrong, then do not add it.
        """

    def transform_img_objs(self, img_objects):
        a = []
        for i in img_objects:
            a.append(f"{i['name']}: {i['svg']}")
        return "\n".join(a)

    def get_rendered_prompt(self, instruction=None):
        print("instruction:", instruction)
        t = Template(self.prompt_template)
        data = {"img_objects": self.img_objects, "instruction": instruction}
        res = t.render(data)
        return res

    def get_completion(self, messages):
        response = openai.ChatCompletion.create(
            model="gpt-4",
            temperature=0.9,
            messages=messages,
        )
        return response["choices"][0]["message"]["content"]

    def run_prompt_with_state(self, instruction):
        # Classify instruction
        style_instruction = (
            self.get_completion(
                self.init_messages
                + [
                    {"role": "user", "content": instruction},
                    self.classify_instruction_prompt,
                ]
            )
        )

        if 'NOSTYLE' not in style_instruction:
            self.style_prompt = style_instruction
            return self.style_prompt

        # Get object name
        name = self.get_completion(
            self.init_messages
            + [
                {"role": "user", "content": instruction},
                self.get_name_prompt,
            ],
        )

        # Modify
        if name in self.img_objects:
            svg_prompts = [
                {
                    "role: assistant",
                    f"""Here is the SVG code for {name}: \n {self.img_objects[name]}""",
                },
                self.modify_svg_prompt,
            ]
        # Add
        else:
            svg_prompts = [self.add_svg_prompt]

        response = openai.ChatCompletion.create(
            model="gpt-4",
            temperature=0.9,
            messages=self.init_messages
            + [
                self.get_name_prompt,
                {"role": "assistant", "content": name},
            ]
            + svg_prompts,
        )
        svg = response["choices"][0]["message"]["content"]

        self.img_objects[name] = svg

        return svg


instructions = [
    "draw me a green square on the right side",
    "add a blue rectangle on the top right",
    "stylize it in a way that makes it look like a painting",
    "create an orange star center bottom, to the right of the green square",
]
# %%
if __name__ == "__main__":
    r = PromptManager()
    for i in instructions:
        print(r.run_prompt_with_state(i))

    print(f"All objects: {r.img_objects}")

# %%
