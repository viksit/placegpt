import functools

class Render():
  def __init__(self):
    
    self.img_objects = [
      {"name": "green square", "svg":  "<svg></svg>"},
      {"name": "orange cat wearing a beret", "svg" : "<svg></svg>"},
      {"name": "romantic hazy filter", "svg" : "<svg></svg>"}
    ]
    self.img_objects_list = self.transform_img_objs(self.img_objects)
   
 
    self.instruction = "add a blue sky on top"
    self.prompt_template = f"""
      you are an art model ai. you control a canvas of 1000 by 1000 pixels. this canvas consists of a list of objects on a canvas. each has a name and an SVG definition. users will ask you to update this canvas with different objects. Here are the items currently in this canvas. generate code that will render all these objects on this canvas.

      {self.img_objects_list}

      you have been given an instruction:

      {self.instruction}

      from instruction please add to or modify this image.

      - if it is an instruction to add an item, return the name of the item followed by the SVG for that item, placed as described in the command.
      - if it is an instruction to modify one or more items, output the list of items being modified, and a new list of all modified items with the appropriate modifications.
      """

  def transform_img_objs(self, img_objects):
    a = []
    for i in img_objects:
      a.append(f"{i['name']}: {i['svg']}")
    return "\n".join(a)

  def get_prompt(self):
    return self.prompt_template
  
r = Render()
print(r.get_prompt())
