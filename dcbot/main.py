import discord
from discord import app_commands
from discord.ext import commands
import math

# up up up uppity
class MetricsBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=discord.Intents.default())

bot = MetricsBot()

def calculate_metrics(rounds_played, targets_assassinated, escapes, targets_protected,
                      damage_dealt, final_shots, target_survival, free_for_all_kills,
                      free_for_all_wins, infected_killed, infection_survival, infections,
                      epidemic, xpb_minus_xpa, sdi=1, device="pc"):
    R = rounds_played
    D = damage_dealt
    T = targets_assassinated
    t = target_survival
    F = free_for_all_kills
    w = free_for_all_wins
    i = infected_killed
    s = infection_survival
    I = infections
    E = escapes
    Sf = final_shots
    P = targets_protected
    e_p = epidemic
    X_T = xpb_minus_xpa
    
    R_ad = R - E
    R_g = R_ad - E - t - e_p - s - w

    S_ma = (2 / 3) * (sdi - 1) + 1 if sdi >= 1 else 1 + ((2 / 3) * (sdi - 1) + 1) - 1
    S_mb = (4 / 3) * (sdi - 1) + 1 if sdi >= 1 else 1 + ((4 / 3) * (sdi - 1) + 1) - 1

    g_os = 46 * ((sdi * 5 * Sf + S_ma * 3 * P) / max(1, R_g))
    
    D_avg = D / max(1, (R_ad - (E + t + e_p)))
    
    t_p = (2 * R_ad * (86 * g_os + S_mb * 32 * D_avg) + sdi * 59 * X_T) / (165 * R_ad)
    z_p = (13 / R_ad) * (S_mb * (9 * F + 15 * i + 40 * w + 25 * I + 100 * e_p) + S_ma * 15 * s)
    o_p = (529 / 20) * math.sqrt(t_p + z_p)

    # the weirder the device, the more aura
    boost_multiplier = 1.0
    if device == "phone":
        boost_multiplier = 1.075
    elif device == "tablet":
        boost_multiplier = 1.05
    elif device == "console":
        boost_multiplier = 1.10

    boosted_o_p = o_p * boost_multiplier

    # find how much aura u got
    division = ""
    if boosted_o_p >= 975:
        division = "Kugelblitz (S)"
    elif boosted_o_p >= 935:
        division = "Radiance (A+)"
    elif boosted_o_p >= 870:
        division = "Firestorm (A)"
    elif boosted_o_p >= 820:
        division = "Flashover (A-)"
    elif boosted_o_p >= 765:
        division = "Magnesium (B+)"
    elif boosted_o_p >= 705:
        division = "Thermite (B)"
    elif boosted_o_p >= 635:
        division = "Propane (C)"
    elif boosted_o_p >= 560:
        division = "Wood (D)"
    else:
        division = "Ember (E)"

    x_pr = X_T / max(1, R_ad)

    return {
        "OP": boosted_o_p,
        "TP": t_p,
        "SP": z_p,
        "GO": g_os,
        "AD": D_avg,
        "XPR": x_pr,
        "Division": division,
        "SDI": sdi
    }

@bot.tree.command(name="calc", description="calculate OP from a copypasta")
async def calc(interaction: discord.Interaction, input_data: str):
    try:
        data = input_data.split()
        if len(data) != 16:
            raise ValueError("invalid number of parameters, expected 16 values!!1~!1!!!")

        xpb_minus_xpa = int(data[0])
        rounds_played = int(data[1])
        targets_assassinated = int(data[2])
        escapes = int(data[3])
        targets_protected = int(data[4])
        damage_dealt = int(data[5])
        final_shots = int(data[6])
        target_survival = int(data[7])
        free_for_all_kills = int(data[8])
        free_for_all_wins = int(data[9])
        infected_killed = int(data[10])
        infection_survival = int(data[11])
        infections = int(data[12])
        epidemic = int(data[13])
        sdi = float(data[14])
        device = data[15].lower()

        metrics = calculate_metrics(
            rounds_played, targets_assassinated, escapes, targets_protected,
            damage_dealt, final_shots, target_survival, free_for_all_kills,
            free_for_all_wins, infected_killed, infection_survival, infections,
            epidemic, xpb_minus_xpa, sdi, device
        )

        if metrics:
            embed = discord.Embed(
                title="",
                color=discord.Color.from_rgb(250, 254, 99)
            )

            # Create a formatted code block message with results
            formatted_message = (
                f"```markdown\n"
                f"OP = {int(metrics['OP'])}\n"
                f"TP = {int(metrics['TP'])}, SP = {int(metrics['SP'])}\n"
                f"[GO = {int(metrics['GO'])}], [AD = {int(metrics['AD'])}], [XPR = {int(metrics['XPR'])}]\n"
                f"SDI = {metrics['SDI']:.4f}\n\n"
                f"Division: {metrics['Division']}\n"
                f"```"
            )
            
            embed.description = formatted_message

            # Buttons for links
            desmos_button = discord.ui.Button(style=discord.ButtonStyle.url, label="desmos", url="https://www.desmos.com/calculator/m60vove8wv")
            seths_button = discord.ui.Button(style=discord.ButtonStyle.url, label="alternative", url="https://sethispr.github.io/fos/")

            view = discord.ui.View()
            view.add_item(desmos_button)
            view.add_item(seths_button)

            await interaction.response.send_message(embed=embed, view=view)

        else:
            await interaction.response.send_message("invalid calculation, please check your input.")

    except Exception as e:
        await interaction.response.send_message(f"ULTRA RARE ERROR: {str(e)}")

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"Logged in as {bot.user}")
    
bot.run("realtokenthatimtootiredtomaskinanenv")
