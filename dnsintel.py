
import logging

from dnsintel.lib.config import Config
from dnsintel.lib.sqlpeewee import init_database, MalwareDomains
from dnsintel.lib.util import reload_blacklist_file, restart_dnsmasq

import click
import logzero
from logzero import logger

@click.group()
@click.option("-l", "--loglevel", help="Set loglevel", type=click.Choice(['DEBUG']))
@click.option("-m", "--module", help="Run specific module")
@click.version_option(version="0.5", prog_name="dnsIntel")
@click.pass_context
def main(ctx, loglevel, module):
    """dnsIntel downloads and parses a list of domains from popular threat intel sources,
then transforms the list into a blacklist which can be used by Dnsmasq\n\n-== Made by @mjdubell ==-"""
    ctx.obj = Config()

    if loglevel == "DEBUG":
        logzero.loglevel(logging.DEBUG)
    else:
        logzero.loglevel(logging.INFO)

    ctx.obj.selected_module = module

@main.command('run', short_help='Run the application')
@click.pass_obj
def run(ctx):

    click.secho("[*] Starting dnsIntel...", fg='green')
    init_database()
    sources = ctx.get_sources()

    if ctx.selected_module:
        if ctx.selected_module in ctx.load_modules():
            click.secho(f"[!] Running Module: {ctx.selected_module}...", fg="cyan")
            module = ctx.load_modules()[ctx.selected_module]

            module.run(sources[ctx.selected_module])
        else:
            click.secho(f"[ERROR] {ctx.selected_module} is not a valid module...", fg="red")
    else:

        for name, module in ctx.load_modules().items():
            click.secho(f"[!] Running Module: {name}...", fg="cyan")

            module.run(sources[name])

    #click.secho("[!] Reloading the blacklist file...", fg="green")
    #domains = [mw.domain for mw in MalwareDomains.select(MalwareDomains.domain)]
    #reload_blacklist_file(domains)

    click.secho("[+] dnsIntel Completed", fg='yellow')


@main.command("reload-blacklist", short_help="Reload the blacklist with domains in DB")
@click.pass_obj
def reload_blacklist(ctx):
    click.secho("[!] Reloading the blacklist file...", fg="green")
    
    domains = [mw.domain for mw in MalwareDomains.select(MalwareDomains.domain)]
    reload_blacklist_file(domains)

    click.secho("[+] Reload Complete", fg='yellow')


@main.command("restart-dnsmasq", short_help="Restart the DNSMASQ service")
@click.pass_obj
def reload_dnsmasq(ctx):
    click.secho("[!] Trying to restart Dnsmasq...", fg="green")
    status = restart_dnsmasq()
    if status:
        click.secho("[+] Dnsmasq has been restarted!", fg="yellow")
    else:
        click.secho("[-] Could not restart Dnsmasq", fg="red")


if __name__ == '__main__':
    main()
