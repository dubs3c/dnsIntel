from dnsintel.util.config import Config
from dnsintel.util.sql import SQL
from dnsintel.util.util import reload_blacklist_file, restart_dnsmasq
import logging
import logzero
from logzero import logger
import click

@click.group()
@click.option("-l", "--loglevel", help="Set loglevel", type=click.Choice(['DEBUG']))
@click.option("-m", "--module", help="Run specific module")
@click.option("-f","--force", default=False, help="Force download previously downloaded files", is_flag=True)
@click.option("-g", "--format", help="Which DNS format to use", type=click.Choice(['DNSMASQ', 'BIND']))
@click.version_option(version="0.5", prog_name="dnsIntel")
@click.pass_context
def main(ctx, loglevel, module, force, format):
    """dnsIntel downloads and parses a list of domains from popular threat intel sources,
then transforms the list into a blacklist which can be used by Dnsmasq and BIND.\n\n-== Made by @mjdubell ==-"""
    ctx.obj = Config()

    if loglevel == "DEBUG":
        logzero.loglevel(logging.DEBUG)
    else:
        logzero.loglevel(logging.INFO)

    ctx.obj.selected_module = module
    ctx.obj.force = force
    ctx.obj.FORMAT = format

@main.command('run', short_help='Run the application')
@click.pass_obj
def run(ctx):

    click.secho("[*] Starting dnsIntel...", fg='green')
    SQL().database_init()
    sources = ctx.get_sources()

    if ctx.selected_module:
        if ctx.selected_module in ctx.load_modules():
            module = ctx.load_modules()[ctx.selected_module]
            module.force = ctx.force
            click.secho(f"[!] Running Module: {ctx.selected_module}...", fg="cyan")
            try:
                module.FORMAT = sources[ctx.selected_module]["FORMAT"]
            except Exception as e:
                logger.error("Could not extract FORMAT option from config.json")
                quit()

            module.db.connect()
            module.run(sources[ctx.selected_module])
            module.db.disconnect()
        else:
            click.secho(f"[ERROR] {ctx.selected_module} is not a valid module...", fg="red")
    else:

        for name, module in ctx.load_modules().items():
            click.secho(f"[!] Running Module: {name}...", fg="cyan")
            try:
                module.FORMAT = sources[name]["FORMAT"]
            except Exception as e:
                logger.error("Could not extract FORMAT option from config.json")
                quit()

            module.db.connect()
            module.force = ctx.force
            module.run(sources[name])
            module.db.disconnect()

    click.secho("[+] dnsIntel Completed", fg='yellow')


@main.command("reload-blacklist", short_help="Reload the blacklist with domains in DB")
@click.pass_obj
def reload_blacklist(ctx):
    if ctx.FORMAT:
        click.secho("[!] Reloading the blacklist file...", fg="green")
        sql = SQL()
        sql.connect()
        domains = sql.get_all_domains(ctx.FORMAT)
        reload_blacklist_file(domains)
        sql.disconnect()
    else:
        click.secho("[*] You need to specify which format you want, --format")

    click.secho("[+] Reload Complete", fg='yellow')


@main.command("restart-dnsmasq", short_help="Restart the DNSMASQ service")
@click.pass_obj
def reload_dnsmasq(ctx):
    # TODO - FIX THIS
    click.secho("[!] Trying to restart Dnsmasq...", fg="green")
    status = restart_dnsmasq()
    if status:
        click.secho("[+] Dnsmasq has been restarted!", fg="yellow")
    else:
        click.secho("[-] Could not restart Dnsmasq", fg="red")


if __name__ == '__main__':
    main()
