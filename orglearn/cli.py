import click

@click.group(invoke_without_command=True)
@click.pass_context
def main(ctx):
    """TODO(mato): Description"""
    if ctx.invoked_subcommand is None:
        print('Hello, orglearn')
    else:
        print('Hello, some command')

@main.group(invoke_without_command=True)
@click.pass_context
def gen(ctx):
    """TODO(mato): Description"""
    if ctx.invoked_subcommand is None:
        print('Hello, gen command')
    else:
        print('Hello, gen')

@gen.command()
@click.argument('org_files', type=click.Path(exists=True), nargs=-1)
def anki(org_files):
    """TODO(mato): Description"""
    for f in org_files:
        print('Hello, anki {}'.format(f))

@gen.command()
@click.argument('org_files', type=click.Path(exists=True), nargs=-1)
def map(org_files):
    """TODO(mato): Description"""
    for f in org_files:
        print('Hello, anki {}'.format(f))

@main.command('test')
def test():
    """TODO(mato): Description"""
    print('Hello, test')
