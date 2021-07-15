from discord.ext import commands
from discord.utils import get
import asyncio
import discord


# Check for bonk and releasing from horny jail
def is_authority():
    async def predicate(ctx):
        return "Authority Ping" in [r.name for r in ctx.author.roles]

    return commands.check(predicate)


# Check for banish and releasing from shadow realm
def can_banish():
    async def predicate(ctx):
        return ctx.author.id in [380550351423537153, 363690578950488074] or "A.S.S." in \
               [r.name for r in ctx.author.roles]

    return commands.check(predicate)


# Not an actual check
def jail_roles(member):
    j_roles = [get(member.guild.roles, name="Horny inmate"), get(member.guild.roles, name="Horny Inmate 0001"),
               get(member.guild.roles, name="Horny Inmate 0002"),
               get(member.guild.roles, name="Horny Inmate 0003"),
               get(member.guild.roles, name="MAXIMUM SECURITY HORNY MF"),
               get(member.guild.roles, name="Banished")]
    member_roles = []
    for role in j_roles:
        if role in member.roles:
            member_roles.append(role)
    return member_roles


class Moderation(commands.Cog):
    """BONK! These commands can be used by users with the role Authority Ping to jail and release other users."""

    def __init__(self, bot):
        self.bot = bot
        self.jailed = set()  # Keep track of who's currently in jail for timer release purposes

    @commands.command(
        brief='Sends a member to horny jail',
        usage='owo bonk <user> [cell] [time]',
        help='This command can only be used by people with the role Authority Ping. '
             'It gives a member the Horny inmate role, along with a role for the cell that they\'re assigned to, '
             'defaulting to sending users to cell 1 for 30 minutes. Specify cell using "1", "2", "3", or "max", '
             'and time using a number in minutes.\n'
             '\n'
             '[Examples]\n'
             '[1] owo bonk floop#6996 max 10\n'
             '[2] owo bonk Weebaoo 2\n'
             '[3] owo bonk 409822116955947018')
    @is_authority()
    async def bonk(self, ctx, member: discord.Member, cell='1', sentence_time: int = 30):
        if get(member.guild.roles, name='Server Booster') in member.roles:
            await ctx.channel.send("Server boosters cannot be bonked")
            return
        if get(member.guild.roles, name='Authority Ping') in member.roles:
            await ctx.channel.send("Mods cannot be bonked")
            return
        # Make sure sentence time is positive
        if sentence_time <= 0:
            await ctx.channel.send('?????????????\nPlease jail people for 1 or more minutes')
            return
        # Remove all previous jail roles
        j_roles = jail_roles(member)
        if j_roles:
            for role in j_roles:
                await member.remove_roles(role)
            await ctx.channel.send(f'Freed prisoner... ready for transport')
        # Gets jail roles
        horny_role = get(member.guild.roles, name='Horny inmate')
        if cell.lower() == 'max':
            cell_role = get(member.guild.roles, name='MAXIMUM SECURITY HORNY MF')
            cell = 'maximum security'
            sentence_time = 60
        else:
            cell_role = get(member.guild.roles, name='Horny Inmate 000' + cell)
            cell = 'cell ' + cell
            if cell_role is None:
                await ctx.channel.send("That is not a valid cell")
                return
        await ctx.channel.send(f'Sent {member} to {cell} in horny jail for {sentence_time} minutes')
        await member.add_roles(horny_role, cell_role)  # Bonk
        self.jailed.add(member)
        await asyncio.sleep(sentence_time * 60)  # Start timer
        # And release if not manually released before
        if member in self.jailed:
            await member.remove_roles(horny_role, cell_role)
            await ctx.channel.send(f'Released {member} from horny jail')
            self.jailed.discard(member)

    @commands.command(
        brief='Banishes a member to THE SHADOW REALM™️',
        usage='owo banish <user>',
        help='This mysterious command can only be used by Alain.\n'
             'Basically soft-bans people\n')
    @can_banish()
    async def banish(self, ctx, member: discord.Member):
        role = get(member.guild.roles, name="Banished")
        if role in member.roles:
            await ctx.channel.send(f"{member} is already in THE SHADOW REALM™️")
            return
        if jail_roles(member):
            for r in jail_roles(member):
                await member.remove_roles(r)
            await ctx.channel.send(f'Freed prisoner... ready for transport')
        await member.add_roles(role)
        self.jailed.add(member)
        await ctx.channel.send(f'Banished {member} to THE SHADOW REALM™️')

    @commands.command(
        brief='Releases someone from the depths',
        usage='owo release <user>',
        help='This command can only be used by people with the role Authority Ping.\n'
             'It removes all horny jail roles from a member, and also removes the banished role if the person using the'
             ' command is Alain.')
    @is_authority()
    async def release(self, ctx, member: discord.Member):
        banish_role = get(member.guild.roles, name="Banished")  # Shadow realm role
        if jail_roles(member):  # Only run if the member is in jail
            if banish_role in member.roles:  # Also unbanish if applicable
                if can_banish():
                    await member.remove_roles(banish_role)
                    await ctx.channel.send(f'Released {member} from THE SHADOW REALM™️')
                    self.jailed.discard(member)
                else:
                    await ctx.channel.send('You don\'t have permission to release from THE SHADOW REALM™️')
            if get(member.guild.roles, name="Horny inmate") in member.roles:  # Unbonk
                await ctx.channel.send(f'Released {member} from horny jail')
                self.jailed.discard(member)
        else:
            await ctx.channel.send(f"There is nothing to release {member} from!")
            return

        await member.remove_roles(get(member.guild.roles, name="Horny inmate"),
                                  get(member.guild.roles, name="Horny Inmate 0001"),
                                  get(member.guild.roles, name="Horny Inmate 0002"),
                                  get(member.guild.roles, name="Horny Inmate 0003"),
                                  get(member.guild.roles, name="MAXIMUM SECURITY HORNY MF"))


def setup(bot):
    bot.add_cog(Moderation(bot))
