from render import PromptManager
import click

p = PromptManager()

@click.command()
def interactive_prompt():
    while True:
        instruction = input("Instruction: ")
        res = p.run_prompt_with_state(instruction)


if __name__ == '__main__':
    interactive_prompt()