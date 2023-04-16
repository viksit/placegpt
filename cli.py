import click
from server import handle_instruction

@click.command()
def interactive_prompt():
    while True:
        instruction = input("Instruction: ")
        res = handle_instruction(instruction)
        print(res)


if __name__ == '__main__':
    interactive_prompt()