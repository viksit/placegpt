from render import PromptManager
import click

p = PromptManager()

@click.command()
def interactive_prompt():
    instruction = input("Enter a propmt: ")
    res = p.mutate_prompt_state(instruction)
    print(res)


if __name__ == '__main__':
    interactive_prompt()