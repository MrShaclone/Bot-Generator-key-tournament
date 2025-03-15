import discord
from discord.ext import commands
from discord.ui import Button, View, Select
import random

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

class TorneioView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(GerarChavesButton())

class GerarChavesButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="⚙️ Gerar Chaves", style=discord.ButtonStyle.primary, custom_id="gerar_chaves_button")

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()

        guild = interaction.guild
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            interaction.user: discord.PermissionOverwrite(read_messages=True)
        }
        canal = await guild.create_text_channel(f'chaves-{interaction.user.name}', overwrites=overwrites)
        
        select_menu1 = Select(
            placeholder="Selecione o tamanho da chave (2-26)...",
            options=[
                discord.SelectOption(label=str(i), value=str(i)) for i in range(2, 27)
            ]
        )

        select_menu2 = Select(
            placeholder="Selecione o tamanho da chave (27-50)...",
            options=[
                discord.SelectOption(label=str(i), value=str(i)) for i in range(27, 51)
            ]
        )

        select_menu3 = Select(
            placeholder="Selecione o tamanho da chave (51-64)...",
            options=[
                discord.SelectOption(label=str(i), value=str(i)) for i in range(51, 65)
            ]
        )

        async def select_callback(interaction):
            await interaction.response.defer()
            tamanho_chave = int(interaction.data['values'][0])
            
            await interaction.followup.send(
                f"Informe os nomes dos {tamanho_chave} times, separados por vírgula:", ephemeral=True
            )

            def check(m):
                return m.author == interaction.user and m.channel == interaction.channel

            msg = await bot.wait_for("message", check=check)
            nomes_times = msg.content.split(',')

            if len(nomes_times) != tamanho_chave or len(set(nomes_times)) != len(nomes_times):
                await interaction.followup.send(
                    "Erro: Certifique-se de que a quantidade de times está correta e que os nomes dos times são únicos.",
                    ephemeral=True
                )
                await canal.send("Selecione o tamanho da chave novamente:", view=view)
                return

            random.shuffle(nomes_times)

            if len(nomes_times) % 2 != 0:
                nomes_times.append("BYE")

            chaves = [f"CHAVE {i+1}\n{nomes_times[i*2]} VS {nomes_times[i*2+1]}" for i in range(len(nomes_times) // 2)]
            mensagem_chaves = "\n\n".join(chaves)

            await canal.send(f"**Chaves geradas:**\n{mensagem_chaves}")

            botao_encerrar = Button(label="Encerrar Canal", style=discord.ButtonStyle.danger, emoji="🛑")

            async def encerrar_callback(interaction):
                await canal.delete()

            botao_encerrar.callback = encerrar_callback

            view = View()
            view.add_item(botao_encerrar)

            await canal.send("Clique no botão abaixo para encerrar o canal.", view=view)

        select_menu1.callback = select_callback
        select_menu2.callback = select_callback
        select_menu3.callback = select_callback

        view = View()
        view.add_item(select_menu1)
        view.add_item(select_menu2)
        view.add_item(select_menu3)

        botao_cancelar = Button(label="Cancelar", style=discord.ButtonStyle.danger, emoji="❌")

        async def cancelar_callback(interaction):
            await canal.delete()

        botao_cancelar.callback = cancelar_callback
        view.add_item(botao_cancelar)

        await canal.send("Selecione o tamanho da chave:", view=view)

@bot.event
async def on_ready():
    bot.add_view(TorneioView())
    await bot.change_presence(activity=discord.Game(name="Feito pelo Ricardo"))
    print(f"Bot {bot.user} está online!")

@bot.command()
async def torneio(ctx):
    descricao = (
        "**🎉 Bem-vindo ao Gerador de Chaves para Torneio! 🎉**\n\n"
        "Crie e organize chaves de torneio facilmente!\n"
        "Adicione participantes, escolha o formato e gere as chaves automaticamente.\n"
        "Tudo pronto para um torneio emocionante!\n\n"
        "Clique no botão abaixo para começar."
    )
    embed = discord.Embed(title="Gerador de Chaves para Torneio", description=descricao, color=0x00ff00)
    await ctx.send(embed=embed, view=TorneioView())

# Executar o bot com seu token
bot.run("SEU ID TOKKEN DO BOT")