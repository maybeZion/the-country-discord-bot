import discord
from discord.ext import commands
from pretty_help import PrettyHelp
import os
import json
import jsonpickle
import time
import random

bot = commands.Bot(command_prefix='./')

def save(data, name):
    with open(name, 'w', encoding='utf-8') as f:
        try:
            json.dump(data, f, ensure_ascii=False, indent=4)
        except TypeError:
            json.dump(jsonpickle.encode(data), f, ensure_ascii=False, indent=4)
        print('Saved value "{}" to {}'.format(data, name))

def load(data, name, decode):
    try:
        with open(str(name), 'r', encoding='utf-8') as f:
            if decode:
                data = jsonpickle.decode(json.load(f))
            else:
                data = json.load(f)
            print('loaded data from "{}" to {}'.format(name, data))
    except FileNotFoundError:
        print('File "{}" not found.'.format(name))
    if str(type(data)) != '<class \'NoneType\'>':
        return data
    else:
        pass

@bot.event
async def on_ready():
    print('Logged in.\n----------')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="./help"))

@bot.event
async def on_member_join(member):
    await bot.get_channel(722509365327691918).send("Welcome to The Country, {}. Please read <#722534492274688011>, <#722534511409365132>, and <#725837069192003655>.".format(member.mention))

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None
        self.job1 = Job('factory', 3, 0, [''], 100, {'Citizen': True, 'Vagrant': True, 'Cabinet': True})
        self.job1 = load(self.job1, self.job1.title, True)
        self.job2 = Job('restaurant', 10, 0.2, [''], 50, {'Citizen': True, 'Vagrant': True, 'Cabinet': True})
        self.job2 = load(self.job2, self.job2.title, True)
        self.job3 = Job('construction', 100, 0.4, [''], 25, {'Citizen': True, 'Vagrant': True, 'Cabinet': True})
        self.job3 = load(self.job3, self.job3.title, True)
        self.job4 = Job('office', 400, 0.6, [''], 12, {'Citizen': True, 'Vagrant': True, 'Cabinet': True})
        self.job4 = load(self.job4, self.job4.title, True)
        self.job5 = Job('farm', 800, 0.8, [''], 6, {'Citizen': True, 'Vagrant': True, 'Cabinet': True})
        self.job5 = load(self.job5, self.job5.title, True)
        self.jobs = [self.job1, self.job2, self.job3, self.job4, self.job5]
        self.ledger = {}
        self.ledger = load(self.ledger, 'ledger', False)
        self.clockin = {}
        self.clockin = load(self.clockin, 'clockin', False)
        self.tax = load(self.tax, 'tax', False)
        self.leader = None
        self.leader = load(self.leader, 'leader', False)

    @commands.command()
    async def bal(self, ctx, member : discord.Member = None):
        if member is None:
            try:
                await ctx.send('Your current balance is **{} credits**.'.format(self.ledger[str(ctx.message.author.id)]))
            except KeyError:
                self.ledger[str(ctx.message.author.id)] = 0
                await ctx.send('Your current balance is **{} credits**.'.format(self.ledger[str(ctx.message.author.id)]))
        else:
            try:
                await ctx.send('{}\'s current balance is **{} credits**.'.format(member.name, self.ledger[str(member.id)]))
            except KeyError:
                self.ledger[str(member.id)] = 0
                await ctx.send('{}\'s current balance is **{} credits**.'.format(member.name, self.ledger[str(member.id)]))

    @commands.command()
    async def give(self, ctx, member : discord.Member, amount):
        try:
            if int(amount) > 0:
                amount = int(amount)
                if type(amount) == int and self.ledger[str(ctx.message.author.id)] >= amount:
                    try:
                        self.ledger[str(ctx.message.author.id)] -= amount
                        x = True
                    except KeyError:
                        await ctx.send('You have no money.')
                    if x:
                        try:
                            self.ledger[str(member.id)] += amount
                        except KeyError:
                            self.ledger[str(member.id)] = amount
                        await ctx.send('Gave **{} credits** to {}.'.format(amount, member.name))
                        save(self.ledger, 'ledger')
                else:
                    await ctx.send('You don\'t have enough money to give.')

            else:
                await ctx.send('Please specify a proper amount in your arguments. Do `./help give` for more info.')
                return
        except ValueError:
            await ctx.send('Please specify a proper amount in your arguments. Do `./help give` for more info.')
            return

    @commands.command()
    async def rob(self, ctx, member : discord.Member):
        x = None
        for item in member.roles:
            if 'Rep' in item.name:
                x = True
                break
        for item in ctx.message.author.roles:
            if 'Rep' in item.name:
                x = True
                break
        if not x:
            if random.choice([True, False]):
                try:
                    self.ledger[str(ctx.message.author.id)] -= int(self.ledger[str(ctx.message.author.id)] // 10)
                    self.ledger[str(member.id)] += int(self.ledger[str(member.id)] // 10)
                    await ctx.send('You robbed {} for 10% of their bank account.'.format(member.name))
                except KeyError:
                    await ctx.send('That member has no money.')
            else:
                await ctx.message.author.remove_roles(discord.utils.get(ctx.message.guild.roles, name='Citizen'))
                await ctx.message.author.add_roles(discord.utils.get(ctx.message.guild.roles, name='Vagrant'))
                await ctx.send('The robbery failed, and you have been exiled! The current leader or Party Rep can pardon you.')
        else:
            await ctx.send('You cannot rob, or be robbed, by a Party Rep.')

    @commands.command()
    async def gamble(self, ctx, amount : int):
        x = None
        for item in ctx.message.author.roles:
            if item.name == 'Citizen' and str(ctx.message.author.id) in self.ledger:
                x = True
                break
            elif item.name == 'Citizen':
                self.ledger[str(ctx.message.author.id)] = 0
        if x and amount == 'all':
            x = random.choice([True, False])
            if x:
                self.ledger[str(ctx.message.author.id)] = self.ledger[str(ctx.message.author.id)] * 2
                await ctx.send('You doubled your money! You now have **{} credits.**'.format(self.ledger[str(ctx.message.author.id)]))
            else:
                self.ledger[str(ctx.message.author.id)] = 0
                await ctx.send('You lost all of your credits.')
        elif x and amount <= self.ledger[str(ctx.message.author.id)]:
            x = random.choice([True, False])
            if x:
                self.ledger[str(ctx.message.author.id)] = self.ledger[str(ctx.message.author.id)] * 2
                await ctx.send('You gained **{} credits.**'.format(amount))
            else:
                self.ledger[str(ctx.message.author.id)] = 0
                await ctx.send('You lost **{} credits**.'.format(amount))
        elif x:
            await ctx.send('You don\'t have enough credits to gamble.')
        else:
            await ctx.send('You have no credits')


    @commands.command()
    async def work(self, ctx):
        worked_job = None
        x = None
        for item in self.jobs:
            if ctx.message.author.id in item.currentworkers:
                worked_job = item
                z = int(worked_job.jobpay() * item.tax)
                y = worked_job.jobpay() - z
                try:
                    self.ledger[str(self.leader)] += z
                except KeyError:
                    self.ledger[str(self.leader)] = z
                break
        if worked_job is not None:
            try:
                if self.clockin[str(ctx.message.author.id)] <= time.time() - 3600:
                    x = True
                    self.clockin[str(ctx.message.author.id)] = time.time()
            except KeyError:
                self.clockin[str(ctx.message.author.id)] = time.time()
            if x:
                try:
                    self.ledger[str(ctx.message.author.id)] += int(y)
                except KeyError:
                    self.ledger[str(ctx.message.author.id)] = int(y)
                save(worked_job, worked_job.title)
                await ctx.send('You made **{} credits** working!'.format(int(y)))
            else:
                await ctx.send('Please wait another {} minute(s) before starting your shift.'.format(int((self.clockin[str(ctx.message.author.id)] - (time.time() - 3600)) // 60)))
        else:
            await ctx.send('It seems you have no job. Try `./job search`.')
        save(self.ledger, 'ledger')
        save(self.clockin, 'clockin')

    @commands.group()
    async def job(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send('Your command seems incomplete; try `./help job`')

    @commands.group()
    async def edit(self, ctx):
        x = None
        if ctx.invoked_subcommand is None:
            await ctx.send('Your command seems incomplete; try `./help job`')
        else:
            for role in ctx.message.author.roles:
                if role.name == 'Leader':
                    x = True
                    break
            if x:
                self.temp_leader_bool = True
        for item in (discord.utils.get(ctx.message.guild.roles, name='Leader')).members:
            self.leader = item.id
            save(self.leader, 'leader')
            break

    @edit.command()
    async def title(self, ctx, job, title):
        if self.temp_leader_bool:
            for job in self.jobs:
                if job.title == job:
                    job.title = title
                    save(job, job.title)
                    await ctx.send('Parameters updated.')
        else:
            await ctx.send("Only the current leader can use this command.")

    @edit.command()
    async def pay(self, ctx, job, pay):
        if self.temp_leader_bool:
            for job in self.jobs:
                if job.title == job and job.pay >= 10 * job.maxworkers:
                    job.pay = pay
                    save(job, job.title)
                    await ctx.send('Parameters updated.')
        else:
            await ctx.send("Only the current leader can use this command.")

    @edit.command()
    async def positions(self, ctx, job, maxworkers):
        if self.temp_leader_bool:
            for job in self.jobs:
                if job.title == job and job.maxworkers >= job.pay / 10:
                    job.maxworkers = maxworkers
                    while len(job.currentworkers) > job.maxworkers:
                        job.currentworkers.pop()
                        x += 1
                    save(job, job.title)
                    await ctx.send('Parameters updated.')
                else:
                    await ctx.send('You misspelled the job title, or your parameters are out of range. The amount of workers can only be one-tenth of job\'s pay.')
        else:
            await ctx.send("Only the current leader can use this command.")

    @edit.command()
    async def tax(self, ctx, tax):
        if self.temp_leader_bool and float(tax) < .5:
            self.tax = tax
            save(self.tax, 'tax')
            await ctx.send('Parameters updated.')
        else:
            await ctx.send("You are either not the leader, or your parameters are out of range.")

    @edit.command()
    async def workers(self, ctx, job, workertype, truefalse):
        if self.temp_leader_bool:
            for job in self.jobs:
                if job.title == job and type(truefalse) == bool:
                    if workertype == 'citizen':
                        job.typeworkers['Citizen'] = truefalse
                    elif workertype == 'vagrant':
                        job.typeworkers['Vagrant'] = truefalse
                    elif workertype == 'cabinet':
                        job.typeworkers['Cabinet'] = truefalse
                    save(job, job.title)
                    await ctx.send('Parameters updated.')
        else:
            await ctx.send("Only the current leader can use this command.")

    @job.command()
    async def search(self, ctx):
        x = []
        availablejobs = 0
        for job in self.jobs:
            availablejobs += job.maxworkers - len(job.currentworkers)
            x.append(job.title)
        availablejobs = availablejobs - len(job.currentworkers)
        x = '`, `'.join(x)
        await ctx.send('There are currently **{}** available jobs, spread over **{}** positions:\n`{}`\nDo `./job apply <position>`.'.format(availablejobs, len(self.jobs), x))

    @job.command()
    async def apply(self, ctx, applied_job):
        last_job = None
        for item in self.jobs:
            if ctx.message.author.id in item.currentworkers:
                last_job = item
            if applied_job == item.title:
                applied_job = item
        for item in ctx.message.author.roles:
            if item.name in applied_job.typeworkers:
                citizentype_temp = item
                break
            else:
                citizentype_temp = None
        if type(applied_job) == str:
            await ctx.send('That job doesn\'t exist. Please do `./job search`')
        elif len(applied_job.currentworkers) == applied_job.maxworkers:
            await ctx.send('There are currently no vacancies in this position. Please do `./job search, or try again later.`')
        elif not citizentype_temp:
            await ctx.send('Sorry, you aren\'t eligible for this position.')
        elif applied_job.typeworkers[citizentype_temp.name]:
            if last_job:
                last_job.currentworkers.remove(ctx.message.author.id)
                save(last_job, last_job.title)
            applied_job.currentworkers.append(ctx.message.author.id)
            save(applied_job, applied_job.title)
            await ctx.send('Congratulations, you have a job! You can now do `./work` to work once per hour.')

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.command()
    async def verify(self, ctx):
        await ctx.message.author.add_roles(discord.utils.get(ctx.message.guild.roles, name='Citizen'))
        x = await ctx.message.channel.send("You have been verified.")
        x = [x, ctx.message]
        await ctx.message.channel.delete_messages(x)

    @commands.command()
    async def purge(self, ctx, count : int):
        messages = []
        for role in ctx.message.author.roles:
            if role.name == 'Admin':
                x = True
                break
        if x is None:
            await ctx.send("You don't have permission to use this command.")
        else:
            try:
                async for message in ctx.message.channel.history(limit=count + 1):
                    messages.append(message)
                await ctx.message.channel.delete_messages(messages)
                x = await ctx.send('Purged **{}** messages.'.format(count))
                time.sleep(4)
                await x.delete()
            except TypeError:
                await ctx.send('Please specify the number of messages you want purged (100 max)')

class Leadership(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None
        self.pending = {}
        self.pending = load(self.pending, 'pending', False)

    @commands.group()
    async def party(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send('Your command seems incomplete; try `./help party`')

    @party.command()
    async def join(self, ctx, party : str):
        x = None
        for item in ctx.message.author.roles:
            if 'Citizen' in item.name:
                x = True
            elif 'Party' in item.name:
                await ctx.send('You are already in a party. Do `./party leave`')
                break
        if x:
            if party in 'redyellowbluegreen':
                self.pending[ctx.message.author.name] = party
                await ctx.send('You have been added to the party\'s waiting list.')
                save(self.pending, 'pending')
            else:
                await ctx.send('That party doesn\'t exist. Your options are `red`, `yellow`, `blue`, and `green`.')
        else:
            await ctx.send('You are not a citizen of The Country. Read <#722534492274688011> for more info.')

    @party.command()
    async def resign(self, ctx):
        x = None
        for item in ctx.message.author.roles:
            if item.name == 'Party Rep':
                for i in item.members:
                    i.add_roles(item)
                    break
                x = True
                break
        if not x:
            ctx.send('You are not Party Rep.')

    @party.command()
    async def leave(self, ctx):
        x = None
        y = None
        for item in ctx.message.author.roles:
            if item.name != 'Party Rep' and 'Party' in item.name:
                await ctx.message.author.remove_roles(item)
                await ctx.send('You have been removed from your party. Do `./party join <party>` to join a new one.')
                x = True
                y = True
                break
        if not y:
            await ctx.send('As Party Rep, you cannot leave. Do `./party resign`')
        elif not x:
            await ctx.send('You aren\'t in a party. Do `./party join <party>`.')

    @party.command()
    async def pending(self, ctx):
        pending_members = []
        for item in ctx.message.author.roles:
            if 'Rep' in item.name:
                x = True
            elif 'Party' in item.name:
                y = item
        if x:
            try:
                for item in self.pending:
                    if self.pending[item].capitalize() in y.name:
                        pending_members.append(item)
                if not pending_members:
                    await ctx.send('There are no members waiting to join your party.')
                else:
                    await ctx.send('Here is a list of pending party members:\n{}'.format(', '.join(pending_members)))
            except KeyError:
                await ctx.send('It seems that this member is not in waiting to join your party.')
        else:
            await ctx.send('You do not have permision to use this command.')

    @party.command()
    async def accept(self, ctx, member : discord.Member):
        for item in ctx.message.author.roles:
            if 'Rep' in item.name:
                x = True
            elif 'Party' in item.name:
                y = item
        if x:
            try:
                if self.pending[member.name].capitalize() in y.name:
                    await member.add_roles(y)
                    del self.pending[member.name]
                    try:
                        self.bot.get_cog('Economy').ledger[str(ctx.message.author.id)] += 250
                    except KeyError:
                        self.bot.get_cog('Economy').ledger[str(ctx.message.author.id)] = 250
                    await ctx.send('{} has joined your party!'.format(member))
            except KeyError:
                await ctx.send('It seems that this member is not in waiting to join your party.')
        else:
            await ctx.send('You do not have permission to use this command.')

    @party.command()
    async def kick(self, ctx, member : discord.Member):
        for item in ctx.message.author.roles:
            if item.name == 'Party Rep':
                x = True
        if ctx.message.author == member:
            await ctx.send('You can\'t kick yourself out of the party.')
        elif x:
            for item in member.roles:
                if 'Red' in item.name or 'Green' in item.name or 'Blue' in item.name or 'Yellow' in item.name:
                    if 'Party' in item.name and item in ctx.message.author.roles:
                        await member.remove_roles(item)
                        await ctx.send('{} has been removed from your party.'.format(member.nick))
        else:
            await ctx.send('You do not have permission to use this command.')

    @commands.command()
    async def exile(self, ctx, member : discord.Member):
        x = None
        for item in ctx.message.author.roles:
            if item.name == 'Leader':
                x = True
        if x:
            for item in member.roles:
                if ' Party' in item.name:
                    await member.remove_roles(discord.utils.get(ctx.message.guild.roles, name='Citizen'))
                    await member.remove_roles(item)
                    await member.add_roles(discord.utils.get(ctx.message.guild.roles, name='Vagrant'))
                    x = await ctx.send('{} has been exiled from The Country.'.format(member.mention))

    @commands.command()
    async def pardon(self, ctx, member : discord.Member):
        x = None
        for item in ctx.message.author.roles:
            if item.name == 'Leader' or item.name == 'Party Rep':
                x = True
        if x:
            for item in member.roles:
                if item.name == 'Vagrant':
                    await member.add_roles(discord.utils.get(ctx.message.guild.roles, name='Citizen'))
                    await member.remove_roles(item)
                    x = await ctx.send('{} has been granted a pardon. Welcome back!'.format(member.mention))

class Job:
    def __init__(self, title, pay, tax, currentworkers, maxworkers, typeworkers):
        self.title = title
        self.pay = pay
        self.tax = tax
        self.currentworkers = currentworkers
        self.maxworkers = maxworkers
        self.typeworkers = typeworkers

    def jobpay(self):
        x = random.randint(self.pay - self.pay // 10, self.pay + self.pay // 10)
        return x

if __name__ == '__main__':
    bot.add_cog(Economy(bot))
    bot.add_cog(Moderation(bot))
    bot.add_cog(Leadership(bot))
    bot.run('token')
