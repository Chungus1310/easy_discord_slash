# Easy Discord Slash

A simple and intuitive library for creating Discord slash commands and message commands with discord.py.

## Features

- 🚀 Easy-to-use decorators for creating slash commands and message commands
- 🔄 Custom argument converters
- ⚠️ Flexible error handling
- 📚 Built-in help command generation
- 🔧 Support for both slash commands and traditional message commands
- 🎯 Type hints and argument validation

## Installation

```bash
pip install discord.py
# Clone this repository
git clone https://github.com/Chungus1310/easy_discord_slash.git
```

## Quick Start

```python
import discord
from discord.ext import commands
from slash import CommandCreator

# Set up the bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)
command_creator = CommandCreator(bot)

# Create a slash command
@command_creator.slash_command(name="add", description="Adds two numbers")
async def add_slash(interaction: discord.Interaction, a: int, b: int):
	await interaction.response.send_message(f"The sum is: {a + b}")

# Create a message command
@command_creator.message_command(name="add_message", aliases=["sum"], description="Adds two numbers")
async def add_message(ctx: commands.Context, a: int, b: int):
	await ctx.send(f"The sum is: {a + b}")

# Run the bot
bot.run("YOUR_BOT_TOKEN")
```

## Features in Detail

### Custom Converters

Register custom type converters for command arguments:

```python
def convert_to_uppercase(value: str) -> str:
	return value.upper()

command_creator.register_converter(str, convert_to_uppercase)
```

### Custom Error Handling

Set up custom error handling for all commands:

```python
async def my_error_handler(error: Exception, ctx):
	if isinstance(ctx, discord.Interaction):
		await ctx.response.send_message(f"Oops! Something went wrong: {error}")
	else:
		await ctx.send(f"Oops! Something went wrong: {error}")

command_creator.set_error_handler(my_error_handler)
```

### Built-in Help Command

The library includes a built-in help command generator that provides detailed information about each command:

```python
@command_creator.slash_command(name="help", description="Get help for a command")
async def help_slash(interaction: discord.Interaction, command_name: str = None):
	if command_name:
		help_text = command_creator.generate_help(command_name)
		await interaction.response.send_message(help_text)
	else:
		commands_list = ", ".join(command_creator.commands.keys())
		await interaction.response.send_message(f"Available commands: {commands_list}")
```

## API Reference

### CommandCreator

#### `__init__(bot)`
- Initialize the CommandCreator with a discord.py Bot instance

#### `slash_command(name: str, description: str = None)`
- Decorator for creating slash commands
- Parameters:
  - `name`: The name of the command
  - `description`: The command description (required)

#### `message_command(name: str, aliases: list = None, description: str = None)`
- Decorator for creating traditional message commands
- Parameters:
  - `name`: The name of the command
  - `aliases`: List of command aliases
  - `description`: The command description

#### `register_converter(type_: Type, converter: Callable)`
- Register a custom argument converter
- Parameters:
  - `type_`: The type to convert from
  - `converter`: The conversion function

#### `set_error_handler(handler: Callable)`
- Set a custom error handler for commands
- Parameters:
  - `handler`: Async function that takes (error, context) as parameters

#### `generate_help(command_name: str) -> str`
- Generate a detailed help message for a command
- Parameters:
  - `command_name`: The name of the command to generate help for
- Returns: Formatted help message as string

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

If you encounter any problems or have questions, please open an issue on GitHub.