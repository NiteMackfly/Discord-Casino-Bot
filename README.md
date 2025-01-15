# 🎰 Casino Bot

<div align="center">

[![Python Version](https://img.shields.io/badge/python-3.10.8+-blue.svg)](https://www.python.org/downloads/)
[![Discord.py Version](https://img.shields.io/badge/discord.py-2.4.0-blue.svg)](https://discordpy.readthedocs.io/en/stable/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A feature-rich Discord gambling bot with multiple casino games, originally created by [ConnorSwis](https://github.com/ConnorSwis/casino-bot) and enhanced with new features and improvements.

[Features](#features) • [Games](#available-games) • [Installation](#installation) • [Configuration](#configuration) • [Commands](#commands)

<img src="https://raw.githubusercontent.com/ConnorSwis/casino-bot/main/pictures/blackjack.png" alt="Blackjack Screenshot" width="400"/>
<img src="https://github.com/ConnorSwis/casino-bot/raw/main/pictures/slots.gif" alt="Slots Animation" width="200"/>

</div>

## ✨ Features

- 🎮 Multiple casino games with interactive buttons
- 💾 Persistent SQLite3 database for user balances
- 🚀 Enhanced performance and reliability
- 🛡️ Improved error handling and spam protection
- 🎯 Discord.py 2.4.0 support
- ⚡ Fast response times and optimized database operations

## 🎲 Available Games

- Blackjack
- Slots
- Coin Flip
- Dice Roll
- Roulette
- And more!

## 📋 Requirements

- Python 3.10.8 or higher
- Discord.py 2.4.0
- SQLite3
- Additional dependencies listed in `requirements.txt`

## 🚀 Installation

1. Create a new bot application on the [Discord Developer Portal](https://discord.com/developers)

2. Install Python 3.10.8 or higher:
   ```bash
   # Download from https://python.org
   python --version  # Verify installation
   ```

3. Clone the repository:
   ```bash
   git clone https://github.com/plawandos/Discord-Casino-Bot.git
   cd Discord-Casino-Bot
   ```

4. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Configure the bot:
   - Copy `config.example.yml` to `config.yml`
   - Add your bot token and customize settings

6. Launch the bot:
   ```bash
   cd discord
   python bot.py
   ```

7. Use `$help` in Discord to see available commands

## 🔧 Recent Upgrades

- ✅ Added Roulette game
- ✅ Upgraded to Discord.py 2.4.0
- ✅ Replaced reactions with interactive buttons
- ✅ Enhanced anti-spam protection
- ✅ Improved database performance
- ✅ Added new commands (`$give @user`, `$sellkidneys`)
- ✅ Fixed database locking issues
- ✅ Implemented robust error handling

## 💬 Commands

- `$help` - Display all available commands
- `$balance` - Check your current balance
- `$blackjack <amount>` - Play Blackjack
- `$slots <amount>` - Play Slots
- `$roulette <amount> <bet>` - Play Roulette
- `$flip <amount> <choice>` - Flip a coin
- `$roll <amount> <number>` - Roll dice
- `$give @user <amount>` - Give money to another user
- `$sellkidneys` - Get emergency funds (joke command)

## 🤝 Credits

Original project by [ConnorSwis](https://github.com/ConnorSwis/casino-bot)

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<div align="center">

Made with ❤️ for Discord gaming communities

</div>
