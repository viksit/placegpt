import click
# from . import get_svg

def get_svg():
    return "svg"

@click.command()
def interactive_prompt():
    prompt = input("Enter a propmt: ")
    svg = get_svg()
    print(svg)


if __name__ == '__main__':
    interactive_prompt()