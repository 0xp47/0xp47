#!/usr/bin/env python3
"""
0xp47 Discord Bot Client Template
Utilizes discord.py to serve profile and repository stats directly to Discord channels.
Instructions:
  1. Install dependencies: pip install discord.py requests
  2. Set environment variable: DISCORD_BOT_TOKEN="your-bot-token"
  3. Run the script: python discord_bot.py
"""

import os
import re
import sys
import discord
from discord import app_commands
import requests

TOKEN = os.environ.get("DISCORD_BOT_TOKEN")
REPO_URL = "https://raw.githubusercontent.com/0xp47/0xp47/main/README.md"
PR_PROGRESS_URL = "https://raw.githubusercontent.com/0xp47/0xp47/main/achievements/pull-shark-progress.md"


class Client(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        # Syncs commands globally. May take up to an hour to propagate.
        await self.tree.sync()
        print("Command tree synced globally.")

    async def on_ready(self):
        print(f"Logged in as {self.user} (ID: {self.user.id})")
        print("------")


client = Client()


def parse_waka_stats():
    try:
        res = requests.get(REPO_URL, timeout=10)
        if res.status_code != 200:
            return None
        content = res.text

        # Search for metrics block
        match = re.search(r"WakaTime \(all time\):\s*([^\n|]+)", content)
        waka_time = match.group(1).strip() if match else "Unknown"

        top_lang = "Unknown"
        lang_match = re.search(r"Top Lang\s*:\s*([^\n|]+)", content)
        if lang_match:
            top_lang = lang_match.group(1).strip()

        top_editor = "Unknown"
        editor_match = re.search(r"Top Editor:\s*([^\n|]+)", content)
        if editor_match:
            top_editor = editor_match.group(1).strip()

        return {"waka_time": waka_time, "top_lang": top_lang, "top_editor": top_editor}
    except Exception:
        return None


@client.tree.command(
    name="stats", description="Displays 0xp47's coding stats from WakaTime"
)
async def stats(interaction: discord.Interaction):
    await interaction.response.defer()
    data = parse_waka_stats()

    if not data:
        await interaction.followup.send("❌ Error: Could not fetch stats from GitHub.")
        return

    embed = discord.Embed(
        title="📊 0xp47's Coding Statistics",
        color=discord.Color.blue(),
        url="https://github.com/0xp47/0xp47",
    )
    embed.add_field(name="⏱️ Total Coding Time", value=data["waka_time"], inline=False)
    embed.add_field(name="💻 Top Language", value=data["top_lang"], inline=True)
    embed.add_field(name="✍️ Top Editor", value=data["top_editor"], inline=True)
    embed.set_footer(text="Data fetched from GitHub profile README.")

    await interaction.followup.send(embed=embed)


@client.tree.command(
    name="achievements", description="Shows unlocked GitHub achievements progress"
)
async def achievements(interaction: discord.Interaction):
    await interaction.response.defer()

    try:
        res = requests.get(PR_PROGRESS_URL, timeout=10)
        if res.status_code == 200:
            lines = res.text.strip().split("\n")
            pr_count = len(
                [l for l in lines if l.startswith("pr-") or l.startswith("pr-farm-")]
            )
        else:
            pr_count = 0
    except Exception:
        pr_count = 0

    embed = discord.Embed(
        title="🏆 0xp47's Achievement Progress",
        color=discord.Color.purple(),
        url="https://github.com/0xp47/0xp47",
    )

    # Simple badges logic
    pull_shark_tier = "None"
    if pr_count >= 1024:
        pull_shark_tier = "Gold (1024+ PRs) 🌟"
    elif pr_count >= 128:
        pull_shark_tier = "Silver (128+ PRs) ⭐"
    elif pr_count >= 16:
        pull_shark_tier = "Bronze (16+ PRs) ✨"
    elif pr_count >= 2:
        pull_shark_tier = "Iron (2+ PRs) 🦈"

    embed.add_field(
        name="🦈 Pull Shark Progress",
        value=f"{pr_count} PRs merged. Current tier: **{pull_shark_tier}**",
        inline=False,
    )
    embed.add_field(
        name="🚀 YOLO Badge",
        value="Unlocked (First PR merged without review)",
        inline=False,
    )
    embed.set_footer(text="0xp47 Achievement tracker bot")

    await interaction.followup.send(embed=embed)


@client.tree.command(name="links", description="Show 0xp47 developer and profile links")
async def links(interaction: discord.Interaction):
    embed = discord.Embed(
        title="🌐 0xp47 Developer Hub",
        description="Connect with me across these platforms!",
        color=discord.Color.green(),
    )
    embed.add_field(
        name="🖥️ GitHub Profile",
        value="[github.com/0xp47](https://github.com/0xp47)",
        inline=True,
    )
    embed.add_field(
        name="📁 Portfolio Website",
        value="[0xp47.vercel.app](https://0xp47.vercel.app)",
        inline=True,
    )
    embed.add_field(
        name="🌳 Linktree",
        value="[0xp47.github.io/linktree](https://0xp47.github.io/linktree)",
        inline=False,
    )

    await interaction.response.send_message(embed=embed)


def main():
    if not TOKEN:
        print("Error: DISCORD_BOT_TOKEN environment variable not set.")
        print("Please check the script headers for setup instructions.")
        sys.exit(1)

    client.run(TOKEN)


if __name__ == "__main__":
    main()
