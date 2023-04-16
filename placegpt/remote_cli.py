import click
import requests
import os

SERVER_URL = os.environ.get("URL", "https://figpt.herokuapp.com/api/draw")
 
def run_remote_prompt(instruction):
  data = {"instruction": instruction}
  x = requests.post(SERVER_URL, json = data)
  print("res: ", x)
  
@click.command()
def interactive_prompt():
    while True:
        instruction = input("Instruction: ")
        res = run_remote_prompt(instruction)


if __name__ == '__main__':
    interactive_prompt()