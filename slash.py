import discord
from discord.ext import commands
from discord import app_commands
import inspect
from typing import Any, Callable, Dict, Optional, Type

class CommandCreator:
    def __init__(self, bot):
        """
        Initialize the CommandCreator.
        
        Args:
            bot: The discord.py Bot instance
        """
        self.bot = bot
        self.tree = app_commands.CommandTree(bot)
        self.commands = {}
        self.converters: Dict[Type, Callable] = {}
        self.error_handler: Optional[Callable] = None

    def register_converter(self, type_: Type, converter: Callable):
        """
        Register a custom argument converter.
        
        Args:
            type_: The type to convert from
            converter: The conversion function
        """
        self.converters[type_] = converter

    def set_error_handler(self, handler: Callable):
        """
        Set a custom error handler for commands.
        
        Args:
            handler: Async function that takes (error, context) as parameters
        """
        self.error_handler = handler

    async def _handle_error(self, error: Exception, ctx: Any):
        if self.error_handler:
            await self.error_handler(error, ctx)
        else:
            if isinstance(ctx, discord.Interaction):
                if not ctx.response.is_done():
                    await ctx.response.send_message(f"Error: {str(error)}")
            else:
                await ctx.send(f"Error: {str(error)}")

    def slash_command(self, name: str, description: str = None):
        """
        Decorator for creating slash commands.
        
        Args:
            name: The name of the command
            description: The command description
        """
        if not description:
            raise ValueError("Description is required for slash commands.")
        
        def decorator(func):
            @self.tree.command(name=name, description=description)
            async def wrapper(interaction: discord.Interaction, *args, **kwargs):
                try:
                    # Apply custom converters if available
                    sig = inspect.signature(func)
                    bound = sig.bind(interaction, *args, **kwargs)
                    bound.apply_defaults()
                    for name_, param in sig.parameters.items():
                        if name_ in self.converters:
                            value = bound.arguments[name_]
                            bound.arguments[name_] = self.converters[param.annotation](value)
                    await func(*bound.args, **bound.kwargs)
                except Exception as e:
                    await self._handle_error(e, interaction)
            self.commands[name] = {"type": "slash", "description": description, "func": func}
            return wrapper
        return decorator

    def message_command(self, name: str, aliases: list = None, description: str = None):
        """
        Decorator for creating traditional message commands.
        
        Args:
            name: The name of the command
            aliases: List of command aliases
            description: The command description
        """
        def decorator(func):
            @self.bot.command(name=name, aliases=aliases or [], description=description)
            async def wrapper(ctx: commands.Context, *args, **kwargs):
                try:
                    # Apply custom converters if available
                    sig = inspect.signature(func)
                    bound = sig.bind(ctx, *args, **kwargs)
                    bound.apply_defaults()
                    for name_, param in sig.parameters.items():
                        if name_ in self.converters:
                            value = bound.arguments[name_]
                            bound.arguments[name_] = self.converters[param.annotation](value)
                    await func(*bound.args, **bound.kwargs)
                except Exception as e:
                    await self._handle_error(e, ctx)
            self.commands[name] = {"type": "message", "aliases": aliases or [], "description": description, "func": func}
            return wrapper
        return decorator

    def generate_help(self, command_name: str) -> str:
        """
        Generate a detailed help message for a command.
        
        Args:
            command_name: The name of the command to generate help for
            
        Returns:
            str: Formatted help message
        """
        if command_name not in self.commands:
            return "Command not found."

        command_data = self.commands[command_name]
        help_message = [f"**{command_name}**"]

        # Add command type and description
        if command_data["type"] == "slash":
            help_message.append("Type: Slash Command")
            if "description" in command_data and command_data["description"]:
                help_message.append(f"Description: {command_data['description']}")
        elif command_data["type"] == "message":
            help_message.append("Type: Message Command")
            if "description" in command_data and command_data["description"]:
                help_message.append(f"Description: {command_data['description']}")
            if "aliases" in command_data and command_data["aliases"]:
                help_message.append(f"Aliases: {', '.join(command_data['aliases'])}")

        # Add parameter information
        sig = inspect.signature(command_data["func"])
        params = sig.parameters
        if len(params) > 1:  # More than just ctx or interaction
            help_message.append("\nArguments:")
            for name, param in params.items():
                if name in ('self', 'ctx', 'interaction'):
                    continue
                
                # Get parameter type
                param_type = param.annotation.__name__ if param.annotation != inspect.Parameter.empty else 'Any'
                
                # Get default value
                default = param.default
                if default == inspect.Parameter.empty:
                    default_str = "Required"
                else:
                    default_str = f"Optional (default: {default})"
                
                # Check if there's a custom converter
                converter_note = ""
                if param.annotation in self.converters:
                    converter_note = " (Custom converter available)"
                
                help_message.append(
                    f"- `{name}`: {param_type} ({default_str}){converter_note}"
                )

        return "\n".join(help_message)

if __name__ == '__main__':
    # Example usage
    intents = discord.Intents.default()
    intents.message_content = True
    bot = commands.Bot(command_prefix="!", intents=intents)
    command_creator = CommandCreator(bot)

    @command_creator.slash_command(name="add", description="Adds two numbers")
    async def add_slash(interaction: discord.Interaction, a: int, b: int):
        await interaction.response.send_message(f"The sum is: {a + b}")

    @command_creator.message_command(name="add_message", aliases=["sum"], description="Adds two numbers")
    async def add_message(ctx: commands.Context, a: int, b: int):
        await ctx.send(f"The sum is: {a + b}")

    @command_creator.slash_command(name="help", description="Get help for a command")
    async def help_slash(interaction: discord.Interaction, command_name: str = None):
        if command_name:
            help_text = command_creator.generate_help(command_name)
            await interaction.response.send_message(help_text)
        else:
            commands_list = ", ".join([cmd for cmd in command_creator.commands.keys() if cmd != "help"])
            await interaction.response.send_message(
                f"Available commands: {commands_list}\n"
                "Use /help <command_name> to get detailed information about a specific command."
            )

    @bot.event
    async def on_ready():
        print(f'Logged in as {bot.user} (ID: {bot.user.id})')
        await command_creator.tree.sync()

    bot.run("YOUR_BOT_TOKEN")