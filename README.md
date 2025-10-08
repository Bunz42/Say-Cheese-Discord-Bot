# Say Cheese! Discord Bot 📸🐀

A fun and interactive Discord bot based on an original game concept called "Say Cheese!" Players can collect different types of rats by taking photos of them when they spawn in your Discord server. Build your collection, earn tokens, and compete with friends!

## 🎮 Features

### Core Gameplay
- **Rat Spawning System**: Rats randomly appear in designated channels after a certain number of messages
- **Photo Capture Mechanic**: Capture rats by typing `sc~capture` when they appear
- **Collection System**: Build your personal photo board with different rat types
- **Rarity System**: Collect Common, Rare, and Legendary rats, each with unique drop rates

### Economy System
- **Token Currency**: Earn tokens by capturing rats
- **Daily Rewards**: Claim 500 tokens daily with a 24-hour cooldown
- **Balance Tracking**: Check your current token balance anytime

### Available Rats
- **Rat** (Common) - Drops 10-50 tokens
- **Disco Rat** (Rare) - Drops 50-150 tokens  
- **Quantum Rat** (Legendary) - Drops 200-500 tokens

## 🛠️ Prerequisites

Before you begin, ensure you have the following installed:
- **Python 3.8+** (recommended: Python 3.10 or higher)
- **pip** (Python package manager)
- **Discord Bot Token** (see [Discord Developer Portal](https://discord.com/developers/applications))

## 📦 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Bunz42/Say-Cheese-Discord-Bot.git
   cd Say-Cheese-Discord-Bot
   ```

2. **Install required dependencies**
   ```bash
   pip install discord.py python-dotenv
   ```

3. **Set up your Discord bot**
   - Go to the [Discord Developer Portal](https://discord.com/developers/applications)
   - Create a new application
   - Navigate to the "Bot" section and create a bot
   - Copy your bot token

4. **Configure environment variables**
   - Create a `.env` file in the root directory:
     ```
     DISCORD_TOKEN=your_bot_token_here
     ```

5. **Configure spawn channel**
   - Edit `discord_bot/cogs/spawning.py`
   - Replace the `SPAWN_CHANNEL_ID` value with your Discord channel ID:
     ```python
     SPAWN_CHANNEL_ID = your_channel_id_here
     ```
   - To get a channel ID: Enable Developer Mode in Discord → Right-click channel → Copy ID

## 🚀 Running the Bot

1. **Start the bot**
   ```bash
   cd discord_bot
   python bot.py
   ```

2. **Verify the bot is running**
   - You should see: `[Bot Name] has connected to Discord!`
   - You should see: `All Cogs loaded successfully!`

## 📝 Commands

All commands use the prefix `sc~`

### Collection Commands
- `sc~capture` - Capture a rat that has appeared in the channel
- `sc~myrats` or `sc~rats` - View your photo board with all captured rats

### Economy Commands
- `sc~daily` - Claim your daily reward of 500 tokens (24-hour cooldown)
- `sc~balance` or `sc~bal` - Check your current token balance

## 📁 Project Structure

```
Say-Cheese-Discord-Bot/
├── discord_bot/
│   ├── bot.py                 # Main bot entry point and setup
│   ├── cogs/
│   │   ├── spawning.py        # Rat spawning and collection logic
│   │   └── economy.py         # Token economy and daily rewards
│   └── rat_collection.db      # SQLite database (auto-generated)
└── README.md                  # This file
```

## 🗄️ Database Schema

The bot uses SQLite with two main tables:

### `rats` Table
- `user_id` - Discord user ID
- `rat_name` - Name of the captured rat
- `captured_at` - Timestamp of capture

### `economy` Table
- `user_id` - Discord user ID (Primary Key)
- `balance` - Current token balance
- `last_claim_time` - Timestamp of last daily claim

## 🎯 How It Works

1. **Spawning**: After users send messages in the spawn channel, a rat will randomly appear
2. **Capturing**: The first user to type `sc~capture` gets the rat and receives tokens
3. **Collection**: All captured rats are saved to your personal photo board
4. **Economy**: Earn tokens from captures and daily rewards to use in future features

## 🔮 Future Improvements

- Trading system between players
- Shop system to spend tokens
- More rat varieties with unique attributes
- Leaderboards and statistics
- Customizable spawn rates per rarity
- Image support for rat appearances
- Achievement system

## ⚙️ Configuration Options

You can customize various aspects in `discord_bot/cogs/spawning.py`:

- **Spawn Threshold**: Change `self.spawn_threshold` to adjust how many messages trigger a spawn
- **Rat Data**: Modify `COLLECTIBLE_DATA` to add new rats or adjust rarities and rewards
- **Daily Reward**: Edit the `reward` variable in `economy.py` to change daily token amounts

## 🐛 Troubleshooting

**Bot doesn't respond to commands**
- Verify the bot has "Message Content Intent" enabled in Discord Developer Portal
- Check that the bot has proper permissions in your server

**Rats don't spawn**
- Ensure `SPAWN_CHANNEL_ID` is correctly set to your channel's ID
- Verify you're sending messages in the correct channel
- Check that the bot is online and running

**Database errors**
- Delete `rat_collection.db` to reset (warning: this deletes all user data)
- Ensure the bot has write permissions in its directory

## 📄 License

This is a personal project by Bunz42. Feel free to use and modify for your own Discord servers.

## 🤝 Contributing

This bot is currently under development. Suggestions and contributions are welcome!

## 📧 Support

For issues or questions, please open an issue on the GitHub repository.

---

**Note**: This bot is a work in progress. Some features are still being developed and refined. Image URLs for rats are not yet configured.