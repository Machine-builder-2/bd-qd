import os
from aiohttp.client import request
import discord
from discord import DMChannel

import json

import base64

import random

from machine_id import decrypt as machine_id_decrypt
from machine_id import caesar_string as string_letters




'''

TODO

check if purchase already exists
based on discord username, and ask
the user if they want to update their
existing purchase request

bot also needs to ask user for paypal
email or some other form of payment
identification. Without this, I can't
tell who payed for what

'''





current_directory = os.getcwd()

def local_fp(relative_fp:str):
    return os.path.join(current_directory, relative_fp)

local_fp_data = local_fp('data.json')

if not os.path.exists(local_fp_data):
    data_base = {
        'pending_purchases': [],
        'verified_purchases': []
    }
    with open(local_fp_data,'w') as f:
        json.dump(data_base, f, indent=4)

class stored_data:
    data = {}

    def load():
        with open(local_fp_data,'r') as f:
            stored_data.data = json.load(f)
    def dump():
        with open(local_fp_data,'w') as f:
            json.dump(stored_data.data, f, indent=4)

stored_data.load()

def random_id(length:int=16):
    return ''.join([random.choice(string_letters) for _ in range(length)])


from update_sub_modules import modules

def decode_purchase_code(code):
    try:
        b64 = base64.b64decode(code).decode()
        return json.loads(b64)
    except:
        return None


def price_string(price:int):
    price_str = 'USD$'+str(price)
    if not '.' in price_str:
        return price_str+'.00'
    before,after = price_str.split('.',1)
    after = after.ljust(2,'0')
    return before+'.'+after


def generate_modules_cart(module_uids):
    total_price = 0
    modules_list = '```'
    for uid in module_uids:
        matching_modules = [m for m in modules if m['uid'] == uid]
        if len(matching_modules) == 0: continue
        m = matching_modules[0]
        name,price = m['name'],m['price']
        price_str = price_string(price).ljust(14,' ')
        modules_list += f'• {price_str} {name}\n'
        total_price += price
    modules_list += '\n'
    modules_list += 'Sub-total        '+price_string(total_price)
    modules_list += '```'
    return modules_list, total_price


TOKEN = open('./token','r').readline().strip()

class Bot(discord.Client):
    async def on_ready(self):
        print(f'{self.user} has connected to Discord.')

        await self.change_presence(
            activity=discord.Activity(
                type=discord.ActivityType.watching,
                name="for purchase requests - DM me a purchase code!"
            )
        )
    
    async def send_embed(
        self,
        embed_title:str,
        embed_text:str,
        channel):

        embed = discord.Embed(
            title=embed_title,
            description=embed_text,
            color=discord.Colour.from_rgb(36,69,145)
        )
        await channel.send(embed=embed)
    
    async def on_message(self, message):
        author = message.author

        user_name = author.name
        user_disc = author.discriminator
        author_name_str = f'@{user_name}#{user_disc}'

        if author == self.user:
            return
        
        channel = message.channel
        if (str(channel.type) != 'private') and (author.id != 385916016569614336):
            # not a DM channel
            return

        mb = await self.fetch_user(385916016569614336)
        content = message.content

        if author.id == 385916016569614336:


            
            # handle validation of purchase requests,
            # only if the message author is me - MACHINE_BUILDER
            # since obviously only I should be able to validate
            # purchases



            if content.startswith('!validate '):
                request_id = content.split('!validate ',1)[-1]

                matching_request = None
                for purchase in stored_data.data['pending_purchases']:
                    if purchase['request_id'] == request_id:
                        matching_request = purchase
                        break
                
                if matching_request is None:
                    embed = discord.Embed(
                        title="Purchase Request Validator",
                        description=(
                            "No purchase was found with that request id"),
                        color=discord.Colour.from_rgb(232, 21, 21)
                    )
                    await channel.send(embed=embed)
                    return
                
                rqi_message_id = matching_request['request_info_message']

                rqi_message = await DMChannel.fetch_message(mb, rqi_message_id)
                embed_info = rqi_message.embeds[0].to_dict()

                embed = discord.Embed(
                    title='Purchase Request (Validated)',
                    description=embed_info['description'],
                    color=discord.Colour.from_rgb(0, 255, 17)
                )

                await rqi_message.edit(embed=embed)

                # also send an embed to the user who originally
                # initialised the purchase request telling them
                # that it has been validated

                modules_list, total_price = generate_modules_cart(
                    matching_request['module_uids'])

                embed = discord.Embed(
                    title='Purchase Request (Validated)',
                    description=(
                        "Your purchase request was validated, "
                        "Here is your order summary :\n"
                        ""+modules_list+"\n"
                        "You should now have access to the "
                        "modules in Bedrock Quickdev"
                    ),
                    color=discord.Colour.from_rgb(0, 255, 17)
                )

                DM_user = await self.fetch_user(matching_request['user_id'])
                await DMChannel.send(
                    DM_user,
                    embed=embed)

                purchase_information = {
                    'purchaser_id': matching_request['user_id'],
                    'purchaser_name': matching_request['discord_name'],
                    'machine_id': matching_request['machine_id'],
                    'modules_owned': matching_request['module_uids']
                }

                a = [p for p in stored_data.data['verified_purchases'] if (
                    p['machine_id'] == matching_request['machine_id'])]
                
                if len(a) > 0:
                    matching_purchase = a[0]
                else:
                    matching_purchase = None

                if matching_purchase is not None:
                    purchase_information['modules_owned'].extend(
                        [muid for muid in matching_purchase['modules_owned'] if (
                        not muid in purchase_information['modules_owned']
                        )])
                    stored_data.data['verified_purchases'].remove(matching_purchase)
                
                stored_data.data['pending_purchases'].remove(matching_request)
                stored_data.data['verified_purchases'].append(purchase_information)
                stored_data.dump()



        # add a !cancel command to cancel a purchase request
        # should look for a pending purchase form the specific user,
        # by first checking their discord name,
        # and if there are multiple pending purchases under their name,
        # it'll ask them for the specific machine id of the purchase
        # that they want to cancel



        decoded_purchase = decode_purchase_code(content)

        if decoded_purchase is not None:
            
            module_uids = decoded_purchase['module_uids']

            if len(module_uids) == 0:
                embed = discord.Embed(
                    title="Purchase Code Confirmation",
                    description=(
                        "It seems like you didn't select any modules. "
                        "Please select at least 1 and try again"),
                    color=discord.Colour.from_rgb(232, 21, 21)
                )
                await channel.send(embed=embed)
                return

            user_id = author.id

            modules_list, total_price = generate_modules_cart(module_uids)

            purchase_request = {
                'user_id': user_id,
                'discord_name': author_name_str,
                'machine_id': None,
                'payment': price_string(total_price),
                'request_id': random_id(),
                'p_payment_id': None,
                'module_uids': module_uids
            }

            embed_description = ''
            embed_description += 'Here\'s a list of all of the modules you selected.\n'
            embed_description += 'Make sure this is correct before proceeding.\n'
            embed_description += modules_list
            
            embed = discord.Embed(
                title="Purchase Code Confirmation",
                description=embed_description,
                color=discord.Colour.from_rgb(36,69,145)
            )

            embed.add_field(
                name="Is the list above correct?",
                value=(
                    "If it is, please react with :white_check_mark: , "
                    "and if it's not correct, please re-select whichever "
                    "modules you'd like on the website, and resend the "
                    "new purchase code.\n\n"
                    "(modules you already own will be checked in the "
                    "next step and deducted from the total cost)"),
                inline=False
            )

            sent_message = await channel.send(embed=embed)
            
            await sent_message.add_reaction('✅')

            def check_reaction(reaction, user):
                return (
                    user.id == author.id and reaction.emoji == '✅' and
                    reaction.message.id == sent_message.id)
            
            try:
                await self.wait_for('reaction_add', timeout=25, check=check_reaction)
                await sent_message.remove_reaction('✅', self.user)

            except:
                await sent_message.remove_reaction('✅', self.user)
                embed = discord.Embed(
                    title="Purchase Code Confirmation",
                    description='Purchase code confirmation has timed out.',
                    color=discord.Colour.from_rgb(232, 21, 21)
                )
                await channel.send(embed=embed)
                return
            


            # check if the user has pending purchases,
            # and ask them if they'd like to overwrite
            # if there's already one under their discord name

            all_pending_purchases = stored_data.data['pending_purchases']
            users_pending_purchases = [purchase for purchase in all_pending_purchases if (
                purchase['discord_name'] == purchase_request['discord_name'])]

            if len(users_pending_purchases) > 0:
                embed = discord.Embed(
                    title="Purchase Code Confirmation",
                    description=(
                        'You already have a pending purchase. '
                        'Continuing with this purchase request '
                        'will overwrite the existing one.\n\n'
                        'react with :white_check_mark: if you\'d '
                        'like to overwrite the existing purchase '
                        'request with this one.'),
                    color=discord.Colour.from_rgb(36,69,145)
                )
                overwrite_confirm_msg = await channel.send(embed=embed)
            
                await overwrite_confirm_msg.add_reaction('✅')

                def check_reaction(reaction, user):
                    return (
                        user.id == author.id and reaction.emoji == '✅' and
                        reaction.message.id == overwrite_confirm_msg.id)

                # wait for check mark reaction for yes
            
                try:
                    await self.wait_for('reaction_add', timeout=25, check=check_reaction)
                    await overwrite_confirm_msg.remove_reaction('✅', self.user)

                except:
                    await overwrite_confirm_msg.remove_reaction('✅', self.user)
                    embed = discord.Embed(
                        title="Purchase Code Confirmation",
                        description='Purchase code confirmation has timed out.',
                        color=discord.Colour.from_rgb(232, 21, 21)
                    )
                    await channel.send(embed=embed)
                    return
                
                # remove other pending purchases from this user
                for purchase in users_pending_purchases:
                    try:
                        rqi_message_id = purchase['request_info_message']

                        rqi_message = await DMChannel.fetch_message(mb, rqi_message_id)
                        embed_info = rqi_message.embeds[0].to_dict()

                        embed = discord.Embed(
                            title='Purchase Request (Overwritten)',
                            description=embed_info['description'],
                            color=discord.Colour.from_rgb(232, 21, 21)
                        )

                        await rqi_message.edit(embed=embed)

                    except Exception as e:
                        print("error when editing previous purchase confirm message :", e)

                    stored_data.data['pending_purchases'].remove(purchase)
                stored_data.dump()



            embed = discord.Embed(
                title="Machine ID Confirmation",
                description=(
                    "Send your Machine ID. You can check your Machine ID by "
                    "running Bedrock Quickdev and checking the console output."),
                color=discord.Colour.from_rgb(36,69,145)
            )

            await channel.send(embed=embed)

            def check_message(other_msg):
                return other_msg.author == author
            
            try:
                other_msg = await self.wait_for('message', timeout=60, check=check_message)
                machine_id = other_msg.content.strip()
                
            except:
                embed = discord.Embed(
                    title="Machine ID Confirmation",
                    description=(
                        "Machine ID confirmation timed out."),
                    color=discord.Colour.from_rgb(232, 21, 21)
                )
                await channel.send(embed=embed)
                return

            decoded_machine_id = machine_id_decrypt(machine_id)
            if decoded_machine_id is not None:
                purchase_request['machine_id'] = decoded_machine_id

            if purchase_request['machine_id'] is None:
                embed = discord.Embed(
                    title="Machine ID Confirmation",
                    description=(
                        "The Machine ID you provided is invalid."),
                    color=discord.Colour.from_rgb(232, 21, 21)
                )
                await channel.send(embed=embed)
                return
            
            # check if we need to remove any already owned modules #


            previous_purchases = [p for p in stored_data.data['verified_purchases'] if (
                p['machine_id'] == decoded_machine_id
            )]
            if len(previous_purchases) > 0:
                current_purchase = previous_purchases[0]
            else:
                current_purchase = None
            
            if current_purchase is not None:
                modules_owned = current_purchase['modules_owned']

                removed_modules = False
                deducted_modules = 0
                new_modules = []
                for muid in module_uids:
                    if not muid in modules_owned:
                        new_modules.append(muid)
                    else:
                        removed_modules = True
                        deducted_modules += 1

                if len(new_modules) == 0:
                    embed = discord.Embed(
                        title="Pre-owned Module Check",
                        description=(
                            "You already own all of the modules that "
                            "you're trying to purchase, so your purchase "
                            "request has been cancelled."),
                        color=discord.Colour.from_rgb(232, 21, 21)
                    )
                    await channel.send(embed=embed)
                    return
                
                elif removed_modules:
                    modules_cart,t = generate_modules_cart(new_modules)
                    embed = discord.Embed(
                        title="Pre-owned Module Check",
                        description=(
                            f"You already own {deducted_modules} of the modules that "
                            "you're trying to purchase, so they have been "
                            "removed from the purchase request. Here is a "
                            "new list of modules you'll be buying :\n"
                            ""+modules_cart+""),
                        color=discord.Colour.from_rgb(36,69,145)
                    )
                    await channel.send(embed=embed)

                    purchase_request['module_uids'] = new_modules
                    purchase_request['payment'] = price_string(t)



            embed = discord.Embed(
                title="Personal Payment Identification",
                description=(
                    "Your Machine ID has been set.\n\n"
                    "When you make your payment, please send "
                    "your discord name with the purchase - this will "
                    "help MACHINE_BUILDER identify your purchase.\n\n"
                    "Please send a method of identification, "
                    "such as your paypal email address, your "
                    "first name, or another form of "
                    "identification that MACHINE_BUILDER "
                    "will be able to recognise in your "
                    "payment - this is just incase the payment "
                    "service does not allow you to send your discord name "
                    "when you make the payment, so that MACHINE_BUILDER "
                    "still has a way to identify the purchase."),
                color=discord.Colour.from_rgb(36,69,145)
            )
            await channel.send(embed=embed)


            def check_message(other_msg):
                return other_msg.author == author
            
            try:
                other_msg = await self.wait_for('message', timeout=60, check=check_message)
                p_payment_id = other_msg.content.strip()
                purchase_request['p_payment_id'] = p_payment_id
                
            except:
                embed = discord.Embed(
                    title="Personal Payment Identification",
                    description=(
                        "Personal payment identification timed out."),
                    color=discord.Colour.from_rgb(232, 21, 21)
                )
                await channel.send(embed=embed)
                return


            embed = discord.Embed(
                title="Personal Payment Identification",
                description=(
                    "Your personal payment identification has been set. "
                    f"Please send a payment of {purchase_request['payment']} "
                    "to MACHINE_BUILDER, and then you will gain "
                    "access to the requested modules once "
                    "the payment is processed manually."),
                color=discord.Colour.from_rgb(0, 255, 17)
            )
            await channel.send(embed=embed)


            try:

                embed_content = (
                    "```"
                    "Request Information\n"
                    "===================\n"
                    f" discord_name : {purchase_request['discord_name']}\n"
                    f" user_id      : {purchase_request['user_id']}\n"
                    f" machine_id   : {purchase_request['machine_id']}\n"
                    f" payment      : {purchase_request['payment']}\n"
                    f" request_id   : {purchase_request['request_id']}\n"
                    f" p_payment_id : {purchase_request['p_payment_id']}"
                    "```")

                print('creating embed...')

                embed = discord.Embed(
                    title="Purchase Request",
                    description=embed_content,
                    color=discord.Colour.from_rgb(255, 230, 0)
                )

                request_info_message = await DMChannel.send(mb, embed=embed)
                print('sent payment request embed')

                purchase_request['request_info_message'] = request_info_message.id
                stored_data.data['pending_purchases'].append(purchase_request)
                stored_data.dump()
            
            except Exception as e:
                print("error when sending payment request info to MACHINE_BUILDER :", e)


bot = Bot()
bot.run(TOKEN)