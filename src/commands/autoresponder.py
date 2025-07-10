"""
Autoresponder management commands for Discord Anti-Phishing Bot
"""
import discord
import logging
from discord import app_commands
from typing import Optional

from guild_config import (
    add_autoresponder_rule,
    remove_autoresponder_rule,
    get_autoresponder_rules,
    toggle_autoresponder_rule,
    get_autoresponder_rule_count,
    edit_autoresponder_rule
)
from src.core.config import config
from src.features.autoresponder import autoresponder_engine

logger = logging.getLogger(__name__)

# Autoresponder command group
autoresponder_group = app_commands.Group(name="autoresponder", description="Manage autoresponder rules for this server")


def _check_permissions(interaction: discord.Interaction) -> bool:
    """Check if user has manage_messages permission"""
    if not interaction.guild or not isinstance(interaction.user, discord.Member):
        return False
    
    # Check for dev override
    try:
        from src.commands.dev import has_dev_override
        if has_dev_override(interaction.user.id):
            return True
    except ImportError:
        pass
    
    return interaction.user.guild_permissions.manage_messages


def _check_guild(interaction: discord.Interaction) -> bool:
    """Check if interaction is in a guild"""
    return interaction.guild is not None


@autoresponder_group.command(name="add", description="Add a new autoresponder rule")
@app_commands.describe(
    rule_name="Name for this autoresponder rule",
    trigger_pattern="Pattern(s) that will trigger the autoresponse (separate multiple with commas)",
    response_message="Message to send when triggered",
    is_regex="Whether the trigger pattern is a regex (default: False)"
)
async def add_rule(interaction: discord.Interaction, rule_name: str, trigger_pattern: str, response_message: str,
                   is_regex: bool = False):
    """Add a new autoresponder rule"""
    try:
        if not _check_guild(interaction):
            await interaction.response.send_message("❌ This command can only be used in a server.", ephemeral=True)
            return

        if not _check_permissions(interaction):
            await interaction.response.send_message("❌ You need 'Manage Messages' permission to use this command.",
                                                    ephemeral=True)
            return

        if not config.AUTORESPONDER_ENABLED:
            await interaction.response.send_message("❌ Autoresponder is disabled on this bot.", ephemeral=True)
            return

        # Check rule limit
        assert interaction.guild is not None  # Type assertion for type checker
        current_count = get_autoresponder_rule_count(interaction.guild.id)
        if current_count >= config.AUTORESPONDER_MAX_RULES_PER_GUILD:
            await interaction.response.send_message(
                f"❌ Maximum number of autoresponder rules reached ({config.AUTORESPONDER_MAX_RULES_PER_GUILD})",
                ephemeral=True)
            return

        # Create the interactive view for case sensitivity selection
        view = AddRuleView(interaction.guild.id, rule_name, trigger_pattern, response_message, is_regex)
        
        embed = discord.Embed(
            title="🤖 Configure Autoresponder Rule",
            description=f"Rule: **{rule_name}**\n\nConfigure the case sensitivity for this rule:",
            color=discord.Color.blue()
        )
        embed.add_field(name="Trigger Pattern", value=f"`{trigger_pattern}`", inline=False)
        embed.add_field(name="Response", value=response_message[:200] + ("..." if len(response_message) > 200 else ""), inline=False)
        embed.add_field(name="Type", value="Regex" if is_regex else "Text", inline=True)
        
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    except Exception as e:
        logger.error(f"Error in add_rule command: {e}")
        await interaction.response.send_message("❌ An error occurred while adding the rule.", ephemeral=True)


@autoresponder_group.command(name="remove", description="Remove an autoresponder rule")
@app_commands.describe(rule_name="Name of the rule to remove")
async def remove_rule(interaction: discord.Interaction, rule_name: str):
    """Remove an autoresponder rule"""
    try:
        if not _check_guild(interaction):
            await interaction.response.send_message("❌ This command can only be used in a server.", ephemeral=True)
            return

        if not _check_permissions(interaction):
            await interaction.response.send_message("❌ You need 'Manage Messages' permission to use this command.",
                                                    ephemeral=True)
            return

        assert interaction.guild is not None  # Type assertion for type checker
        success = remove_autoresponder_rule(interaction.guild.id, rule_name)

        if success:
            await interaction.response.send_message(f"✅ Autoresponder rule **{rule_name}** has been removed.")
        else:
            await interaction.response.send_message(f"❌ No autoresponder rule found with the name **{rule_name}**.",
                                                    ephemeral=True)

    except Exception as e:
        logger.error(f"Error in remove_rule command: {e}")
        await interaction.response.send_message("❌ An error occurred while removing the rule.", ephemeral=True)


@autoresponder_group.command(name="list", description="List all autoresponder rules for this server")
async def list_rules(interaction: discord.Interaction):
    """List all autoresponder rules for this server"""
    try:
        if not _check_guild(interaction):
            await interaction.response.send_message("❌ This command can only be used in a server.", ephemeral=True)
            return

        if not _check_permissions(interaction):
            await interaction.response.send_message("❌ You need 'Manage Messages' permission to use this command.",
                                                    ephemeral=True)
            return

        assert interaction.guild is not None  # Type assertion for type checker
        rules = get_autoresponder_rules(interaction.guild.id)

        if not rules:
            embed = discord.Embed(
                title="📋 Autoresponder Rules",
                description="No autoresponder rules configured for this server.",
                color=discord.Color.blue()
            )
            await interaction.response.send_message(embed=embed, ephemeral=False)
            return

        embed = discord.Embed(
            title="📋 Autoresponder Rules",
            description=f"Found {len(rules)} autoresponder rule(s)",
            color=discord.Color.blue()
        )

        for rule in rules[:10]:  # Limit to first 10 rules to avoid embed limits
            status = "🟢 Enabled" if rule['is_enabled'] else "🔴 Disabled"
            rule_type = "🔤 Regex" if rule['is_regex'] else "📝 Text"
            case_info = " (Case Sensitive)" if rule['case_sensitive'] else ""

            # Handle multiple triggers display
            triggers = rule['trigger_patterns'] if isinstance(rule['trigger_patterns'], list) else [rule['trigger_patterns']]
            trigger_display = ', '.join(triggers)
            if len(trigger_display) > 50:
                trigger_display = trigger_display[:47] + "..."
            
            response_display = rule['response_message'][:100] + ("..." if len(rule['response_message']) > 100 else "")

            embed.add_field(
                name=f"{rule['rule_name']} - {status}",
                value=f"**Type:** {rule_type}{case_info}\n**Trigger:** `{trigger_display}`\n**Response:** {response_display}",
                inline=False
            )

        if len(rules) > 10:
            embed.set_footer(text=f"Showing first 10 of {len(rules)} rules")

        await interaction.response.send_message(embed=embed, ephemeral=False)

    except Exception as e:
        logger.error(f"Error in list_rules command: {e}")
        await interaction.response.send_message("❌ An error occurred while listing rules.", ephemeral=True)


@autoresponder_group.command(name="toggle", description="Enable or disable an autoresponder rule")
@app_commands.describe(
    rule_name="Name of the rule to toggle",
    enabled="True to enable, False to disable"
)
async def toggle_rule(interaction: discord.Interaction, rule_name: str, enabled: bool):
    """Enable or disable an autoresponder rule"""
    try:
        if not _check_guild(interaction):
            await interaction.response.send_message("❌ This command can only be used in a server.", ephemeral=True)
            return

        if not _check_permissions(interaction):
            await interaction.response.send_message("❌ You need 'Manage Messages' permission to use this command.",
                                                    ephemeral=True)
            return

        assert interaction.guild is not None  # Type assertion for type checker
        rules = get_autoresponder_rules(interaction.guild.id)
        current_rule = next((r for r in rules if r['rule_name'] == rule_name), None)

        if not current_rule:
            await interaction.response.send_message(f"❌ No autoresponder rule found with the name **{rule_name}**.",
                                                    ephemeral=True)
            return

        success = toggle_autoresponder_rule(interaction.guild.id, rule_name, enabled)

        if success:
            status = "enabled" if enabled else "disabled"
            await interaction.response.send_message(f"✅ Autoresponder rule **{rule_name}** has been {status}.")
        else:
            await interaction.response.send_message(f"❌ Failed to update rule **{rule_name}**.", ephemeral=True)

    except Exception as e:
        logger.error(f"Error in toggle_rule command: {e}")
        await interaction.response.send_message("❌ An error occurred while toggling the rule.", ephemeral=True)


@autoresponder_group.command(name="test", description="Test an autoresponder rule against a message")
@app_commands.describe(
    rule_name="Name of the rule to test",
    test_message="Message to test against the rule"
)
async def test_rule(interaction: discord.Interaction, rule_name: str, test_message: str):
    """Test an autoresponder rule against a message"""
    try:
        if not _check_guild(interaction):
            await interaction.response.send_message("❌ This command can only be used in a server.", ephemeral=True)
            return

        if not _check_permissions(interaction):
            await interaction.response.send_message("❌ You need 'Manage Messages' permission to use this command.",
                                                    ephemeral=True)
            return

        assert interaction.guild is not None  # Type assertion for type checker
        rules = get_autoresponder_rules(interaction.guild.id)
        rule = next((r for r in rules if r['rule_name'] == rule_name), None)

        if not rule:
            await interaction.response.send_message(f"❌ No autoresponder rule found with the name **{rule_name}**.",
                                                    ephemeral=True)
            return

        # Test the pattern matching
        matches = autoresponder_engine._matches_pattern(test_message, rule)

        embed = discord.Embed(
            title=f"🧪 Test Result for Rule: {rule_name}",
            color=discord.Color.green() if matches else discord.Color.red()
        )

        embed.add_field(name="Test Message", value=f"```{test_message}```", inline=False)
        embed.add_field(name="Trigger Patterns", value=f"`{', '.join(rule['trigger_patterns'])}`", inline=False)
        embed.add_field(name="Match Result", value="✅ Matches" if matches else "❌ No Match", inline=True)
        embed.add_field(name="Rule Type", value="Regex" if rule['is_regex'] else "Text", inline=True)
        embed.add_field(name="Case Sensitive", value="Yes" if rule['case_sensitive'] else "No", inline=True)

        if matches:
            embed.add_field(name="Would Respond With", value=rule['response_message'][:500] + (
                "..." if len(rule['response_message']) > 500 else ""), inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True)

    except Exception as e:
        logger.error(f"Error in test_rule command: {e}")
        await interaction.response.send_message("❌ An error occurred while testing the rule.", ephemeral=True)


@autoresponder_group.command(name="info", description="Get detailed information about an autoresponder rule")
@app_commands.describe(rule_name="Name of the rule to get information about")
async def rule_info(interaction: discord.Interaction, rule_name: str):
    """Get detailed information about an autoresponder rule"""
    try:
        if not _check_guild(interaction):
            await interaction.response.send_message("❌ This command can only be used in a server.", ephemeral=True)
            return

        if not _check_permissions(interaction):
            await interaction.response.send_message("❌ You need 'Manage Messages' permission to use this command.",
                                                    ephemeral=True)
            return

        assert interaction.guild is not None  # Type assertion for type checker
        rules = get_autoresponder_rules(interaction.guild.id)
        rule = next((r for r in rules if r['rule_name'] == rule_name), None)

        if not rule:
            await interaction.response.send_message(f"❌ No autoresponder rule found with the name **{rule_name}**.",
                                                    ephemeral=True)
            return

        embed = discord.Embed(
            title=f"📋 Rule Information: {rule['rule_name']}",
            color=discord.Color.blue()
        )

        embed.add_field(name="Status", value="🟢 Enabled" if rule['is_enabled'] else "🔴 Disabled", inline=True)
        embed.add_field(name="Type", value="🔤 Regex" if rule['is_regex'] else "📝 Text", inline=True)
        embed.add_field(name="Case Sensitive", value="Yes" if rule['case_sensitive'] else "No", inline=True)
        embed.add_field(name="Trigger Patterns", value=f"```{', '.join(rule['trigger_patterns'])}```", inline=False)
        embed.add_field(name="Response Message",
                        value=rule['response_message'][:1000] + ("..." if len(rule['response_message']) > 1000 else ""),
                        inline=False)
        embed.add_field(name="Created", value=rule['created_at'], inline=True)

        await interaction.response.send_message(embed=embed, ephemeral=False)

    except Exception as e:
        logger.error(f"Error in rule_info command: {e}")
        await interaction.response.send_message("❌ An error occurred while getting rule information.", ephemeral=True)


@autoresponder_group.command(name="edit", description="Edit an existing autoresponder rule")
@app_commands.describe(
    rule_name="Name of the rule to edit",
    new_trigger_patterns="New trigger patterns separated by commas (leave blank to keep current)",
    new_response_message="New response message (leave blank to keep current)",
    is_regex="Whether the trigger pattern is a regex"
)
async def edit_rule(interaction: discord.Interaction, rule_name: str, 
                    new_trigger_patterns: str | None = None, new_response_message: str | None = None,
                    is_regex: bool | None = None):
    """Edit an existing autoresponder rule"""
    try:
        if not _check_guild(interaction):
            await interaction.response.send_message("❌ This command can only be used in a server.", ephemeral=True)
            return

        if not _check_permissions(interaction):
            await interaction.response.send_message("❌ You need 'Manage Messages' permission to use this command.",
                                                    ephemeral=True)
            return

        assert interaction.guild is not None  # Type assertion for type checker
        
        # Check if rule exists
        rules = get_autoresponder_rules(interaction.guild.id)
        current_rule = next((r for r in rules if r['rule_name'] == rule_name), None)

        if not current_rule:
            await interaction.response.send_message(f"❌ No autoresponder rule found with the name **{rule_name}**.",
                                                    ephemeral=True)
            return

        # Create the interactive view for editing the rule
        view = EditRuleView(
            interaction.guild.id, 
            rule_name, 
            current_rule,
            new_trigger_patterns, 
            new_response_message, 
            is_regex
        )
        
        embed = discord.Embed(
            title="✏️ Edit Autoresponder Rule",
            description=f"Rule: **{rule_name}**\n\nConfigure the settings for this rule:",
            color=discord.Color.blue()
        )
        
        # Show current values
        current_triggers = ', '.join(current_rule['trigger_patterns']) if isinstance(current_rule['trigger_patterns'], list) else current_rule['trigger_patterns']
        embed.add_field(name="Current Trigger", value=f"`{current_triggers}`", inline=False)
        embed.add_field(name="Current Response", value=current_rule['response_message'][:200] + ("..." if len(current_rule['response_message']) > 200 else ""), inline=False)
        embed.add_field(name="Current Type", value="Regex" if current_rule['is_regex'] else "Text", inline=True)
        embed.add_field(name="Current Case Sensitive", value="Yes" if current_rule['case_sensitive'] else "No", inline=True)
        
        # Show new values if provided
        if new_trigger_patterns or new_response_message or is_regex is not None:
            embed.add_field(name="─────────────────────", value="**Pending Changes:**", inline=False)
            if new_trigger_patterns:
                embed.add_field(name="New Trigger", value=f"`{new_trigger_patterns}`", inline=False)
            if new_response_message:
                embed.add_field(name="New Response", value=new_response_message[:200] + ("..." if len(new_response_message) > 200 else ""), inline=False)
            if is_regex is not None:
                embed.add_field(name="New Type", value="Regex" if is_regex else "Text", inline=True)
        
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    except Exception as e:
        logger.error(f"Error in edit_rule command: {e}")
        await interaction.response.send_message("❌ An error occurred while editing the rule.", ephemeral=True)


# Help command for autoresponder
@app_commands.command(name="autoresponder-help", description="Show detailed help for autoresponder commands")
async def autoresponder_help(interaction: discord.Interaction):
    """Show detailed help for autoresponder commands"""
    try:
        if not _check_permissions(interaction):
            await interaction.response.send_message("❌ You need 'Manage Messages' permission to use this command.",
                                                    ephemeral=True)
            return

        embed = discord.Embed(
            title="🤖 Autoresponder Help",
            description="The autoresponder allows you to automatically respond to messages that match certain patterns.",
            color=discord.Color.blue()
        )

        embed.add_field(
            name="📝 Commands",
            value="""
            `/autoresponder add` - Add a new rule
            `/autoresponder remove` - Remove a rule
            `/autoresponder list` - Show all rules
            `/autoresponder toggle` - Enable/disable a rule
            `/autoresponder test` - Test a rule
            `/autoresponder info` - Get rule details
            `/autoresponder edit` - Edit an existing rule
            """,
            inline=False
        )

        embed.add_field(
            name="🚀 Pattern Types",
            value="""
            **Text**: Simple substring matching
            **Regex**: Advanced pattern matching with regular expressions
            """,
            inline=False
        )

        embed.add_field(
            name="📚 Examples",
            value="""
            Simple text: `hello` matches "hello world"
            Regex: `(?i)help.*` matches "HELP ME" (case insensitive)
            Case sensitive: `Hello` only matches "Hello" (not "hello")
            Multiple triggers: `hello,hi,hey` matches any of these words
            """,
            inline=False
        )

        embed.add_field(
            name="✏️ Editing Rules",
            value="""
            Use `/autoresponder edit` to modify existing rules
            You can change: triggers, response message, regex/text mode, case sensitivity
            Multiple triggers: Separate with commas when editing
            """,
            inline=False
        )

        embed.set_footer(text=f"Cooldown: {config.AUTORESPONDER_COOLDOWN}s between responses per user")

        await interaction.response.send_message(embed=embed)

    except Exception as e:
        logger.error(f"Error in autoresponder_help command: {e}")
        await interaction.response.send_message("❌ An error occurred while showing help.", ephemeral=True)


class AddRuleView(discord.ui.View):
    """Interactive view for adding autoresponder rules with case sensitivity toggle"""
    
    def __init__(self, guild_id: int, rule_name: str, trigger_pattern: str, response_message: str, is_regex: bool):
        super().__init__(timeout=300)
        self.guild_id = guild_id
        self.rule_name = rule_name
        self.trigger_pattern = trigger_pattern
        self.response_message = response_message
        self.is_regex = is_regex
        self.case_sensitive = False  # Default to False
        
        # Create toggle button
        self.toggle_button = discord.ui.Button(
            label="Case Sensitive: OFF",
            style=discord.ButtonStyle.secondary,
            custom_id="toggle_case"
        )
        self.toggle_button.callback = self.toggle_case_sensitivity
        self.add_item(self.toggle_button)
        
        # Create rule button
        create_button = discord.ui.Button(
            label="✅ Create Rule",
            style=discord.ButtonStyle.primary
        )
        create_button.callback = self.create_rule
        self.add_item(create_button)
        
        # Cancel button
        cancel_button = discord.ui.Button(
            label="❌ Cancel",
            style=discord.ButtonStyle.danger
        )
        cancel_button.callback = self.cancel_creation
        self.add_item(cancel_button)
    
    def update_button_labels(self):
        """Update button labels to reflect current state"""
        self.toggle_button.label = f"Case Sensitive: {'ON' if self.case_sensitive else 'OFF'}"
        self.toggle_button.style = discord.ButtonStyle.success if self.case_sensitive else discord.ButtonStyle.secondary
    
    async def toggle_case_sensitivity(self, interaction: discord.Interaction):
        """Toggle case sensitivity setting"""
        self.case_sensitive = not self.case_sensitive
        self.update_button_labels()
        
        embed = discord.Embed(
            title="🤖 Configure Autoresponder Rule",
            description=f"Rule: **{self.rule_name}**\n\nConfigure the case sensitivity for this rule:",
            color=discord.Color.blue()
        )
        embed.add_field(name="Trigger Pattern", value=f"`{self.trigger_pattern}`", inline=False)
        embed.add_field(name="Response", value=self.response_message[:200] + ("..." if len(self.response_message) > 200 else ""), inline=False)
        embed.add_field(name="Type", value="Regex" if self.is_regex else "Text", inline=True)
        embed.add_field(name="Case Sensitive", value="✅ Yes" if self.case_sensitive else "❌ No", inline=True)
        
        await interaction.response.edit_message(embed=embed, view=self)
    
    async def create_rule(self, interaction: discord.Interaction):
        """Create the autoresponder rule with selected settings"""
        try:
            # Validate rule
            is_valid, error_msg = autoresponder_engine.validate_rule(self.trigger_pattern, self.is_regex, self.case_sensitive)
            if not is_valid:
                await interaction.response.send_message(f"❌ Invalid trigger pattern: {error_msg}", ephemeral=True)
                return

            # Validate response
            is_valid, error_msg = autoresponder_engine.validate_response(self.response_message)
            if not is_valid:
                await interaction.response.send_message(f"❌ Invalid response message: {error_msg}", ephemeral=True)
                return

            # Add the rule
            success = add_autoresponder_rule(
                self.guild_id,
                self.rule_name,
                self.trigger_pattern,
                self.response_message,
                self.is_regex,
                self.case_sensitive
            )

            if success:
                embed = discord.Embed(
                    title="✅ Autoresponder Rule Added",
                    color=discord.Color.green(),
                    description=f"Rule **{self.rule_name}** has been created successfully."
                )
                embed.add_field(name="Trigger", value=f"`{self.trigger_pattern}`", inline=False)
                embed.add_field(name="Response",
                                value=self.response_message[:1000] + ("..." if len(self.response_message) > 1000 else ""),
                                inline=False)
                embed.add_field(name="Type", value="Regex" if self.is_regex else "Text", inline=True)
                embed.add_field(name="Case Sensitive", value="Yes" if self.case_sensitive else "No", inline=True)
                
                # Disable all buttons
                self.toggle_button.disabled = True
                for item in self.children:
                    if isinstance(item, discord.ui.Button):
                        item.disabled = True
                
                await interaction.response.edit_message(embed=embed, view=self)
            else:
                await interaction.response.send_message(
                    f"❌ Failed to add rule. A rule with the name **{self.rule_name}** already exists.", ephemeral=True)

        except Exception as e:
            logger.error(f"Error creating autoresponder rule: {e}")
            await interaction.response.send_message("❌ An error occurred while creating the rule.", ephemeral=True)
    
    async def cancel_creation(self, interaction: discord.Interaction):
        """Cancel rule creation"""
        embed = discord.Embed(
            title="❌ Rule Creation Cancelled",
            description="The autoresponder rule was not created.",
            color=discord.Color.red()
        )
        
        # Disable all buttons
        self.toggle_button.disabled = True
        for item in self.children:
            if isinstance(item, discord.ui.Button):
                item.disabled = True
        
        await interaction.response.edit_message(embed=embed, view=self)


class EditRuleView(discord.ui.View):
    """Interactive view for editing autoresponder rules with case sensitivity toggle"""
    
    def __init__(self, guild_id: int, rule_name: str, current_rule: dict, new_trigger_patterns: str | None = None, 
                 new_response_message: str | None = None, is_regex: bool | None = None):
        super().__init__(timeout=300)
        self.guild_id = guild_id
        self.rule_name = rule_name
        self.current_rule = current_rule
        self.new_trigger_patterns = new_trigger_patterns
        self.new_response_message = new_response_message
        self.is_regex = is_regex
        self.case_sensitive = current_rule['case_sensitive']  # Start with current value
        
        # Create toggle button
        self.toggle_button = discord.ui.Button(
            label=f"Case Sensitive: {'ON' if self.case_sensitive else 'OFF'}",
            style=discord.ButtonStyle.success if self.case_sensitive else discord.ButtonStyle.secondary,
            custom_id="toggle_case"
        )
        self.toggle_button.callback = self.toggle_case_sensitivity
        self.add_item(self.toggle_button)
        
        # Apply changes button
        apply_button = discord.ui.Button(
            label="✅ Apply Changes",
            style=discord.ButtonStyle.primary
        )
        apply_button.callback = self.apply_changes
        self.add_item(apply_button)
        
        # Cancel button
        cancel_button = discord.ui.Button(
            label="❌ Cancel",
            style=discord.ButtonStyle.danger
        )
        cancel_button.callback = self.cancel_edit
        self.add_item(cancel_button)
    
    def update_button_labels(self):
        """Update button labels to reflect current state"""
        self.toggle_button.label = f"Case Sensitive: {'ON' if self.case_sensitive else 'OFF'}"
        self.toggle_button.style = discord.ButtonStyle.success if self.case_sensitive else discord.ButtonStyle.secondary
    
    async def toggle_case_sensitivity(self, interaction: discord.Interaction):
        """Toggle case sensitivity setting"""
        self.case_sensitive = not self.case_sensitive
        self.update_button_labels()
        
        embed = discord.Embed(
            title="✏️ Edit Autoresponder Rule",
            description=f"Rule: **{self.rule_name}**\n\nConfigure the settings for this rule:",
            color=discord.Color.blue()
        )
        
        # Show current values
        current_triggers = ', '.join(self.current_rule['trigger_patterns']) if isinstance(self.current_rule['trigger_patterns'], list) else self.current_rule['trigger_patterns']
        embed.add_field(name="Current Trigger", value=f"`{current_triggers}`", inline=False)
        embed.add_field(name="Current Response", value=self.current_rule['response_message'][:200] + ("..." if len(self.current_rule['response_message']) > 200 else ""), inline=False)
        embed.add_field(name="Current Type", value="Regex" if self.current_rule['is_regex'] else "Text", inline=True)
        embed.add_field(name="Original Case Sensitive", value="Yes" if self.current_rule['case_sensitive'] else "No", inline=True)
        
        # Show pending changes
        embed.add_field(name="─────────────────────", value="**Pending Changes:**", inline=False)
        if self.new_trigger_patterns:
            embed.add_field(name="New Trigger", value=f"`{self.new_trigger_patterns}`", inline=False)
        if self.new_response_message:
            embed.add_field(name="New Response", value=self.new_response_message[:200] + ("..." if len(self.new_response_message) > 200 else ""), inline=False)
        if self.is_regex is not None:
            embed.add_field(name="New Type", value="Regex" if self.is_regex else "Text", inline=True)
        
        # Always show case sensitivity as it can be changed
        embed.add_field(name="New Case Sensitive", value=f"✅ Yes" if self.case_sensitive else "❌ No", inline=True)
        
        await interaction.response.edit_message(embed=embed, view=self)
    
    async def apply_changes(self, interaction: discord.Interaction):
        """Apply the changes to the autoresponder rule"""
        try:
            # Prepare trigger patterns
            new_trigger_patterns_list = None
            if self.new_trigger_patterns is not None:
                new_trigger_patterns_list = [p.strip() for p in self.new_trigger_patterns.split(',') if p.strip()]
                # Validate each pattern
                for pattern in new_trigger_patterns_list:
                    effective_regex = self.is_regex if self.is_regex is not None else self.current_rule['is_regex']
                    is_valid, error_msg = autoresponder_engine.validate_rule(pattern, effective_regex, self.case_sensitive)
                    if not is_valid:
                        await interaction.response.send_message(f"❌ Invalid trigger pattern '{pattern}': {error_msg}", ephemeral=True)
                        return

            # Validate new response if provided
            if self.new_response_message is not None:
                is_valid, error_msg = autoresponder_engine.validate_response(self.new_response_message)
                if not is_valid:
                    await interaction.response.send_message(f"❌ Invalid response message: {error_msg}", ephemeral=True)
                    return

            # Determine final case sensitivity (different from original or explicitly changed)
            final_case_sensitive = self.case_sensitive if self.case_sensitive != self.current_rule['case_sensitive'] else None

            # Update the rule
            success = edit_autoresponder_rule(
                self.guild_id,
                self.rule_name,
                new_trigger_patterns=new_trigger_patterns_list,
                new_response_message=self.new_response_message,
                new_is_regex=self.is_regex,
                new_case_sensitive=final_case_sensitive
            )

            if success:
                embed = discord.Embed(
                    title="✅ Autoresponder Rule Updated",
                    color=discord.Color.green(),
                    description=f"Rule **{self.rule_name}** has been updated successfully."
                )
                
                # Show what was changed
                changes = []
                if new_trigger_patterns_list:
                    changes.append(f"**Trigger Patterns:** `{', '.join(new_trigger_patterns_list)}`")
                if self.new_response_message is not None:
                    changes.append(f"**Response:** {self.new_response_message[:200]}{'...' if len(self.new_response_message) > 200 else ''}")
                if self.is_regex is not None:
                    changes.append(f"**Type:** {'Regex' if self.is_regex else 'Text'}")
                if final_case_sensitive is not None:
                    changes.append(f"**Case Sensitive:** {'Yes' if self.case_sensitive else 'No'}")
                
                if changes:
                    embed.add_field(name="Changes Made", value="\n".join(changes), inline=False)
                else:
                    embed.add_field(name="Result", value="No changes were made to the rule.", inline=False)
                
                # Disable all buttons
                self.toggle_button.disabled = True
                for item in self.children:
                    if isinstance(item, discord.ui.Button):
                        item.disabled = True
                
                await interaction.response.edit_message(embed=embed, view=self)
            else:
                await interaction.response.send_message(f"❌ Failed to update rule **{self.rule_name}**.", ephemeral=True)

        except Exception as e:
            logger.error(f"Error editing autoresponder rule: {e}")
            await interaction.response.send_message("❌ An error occurred while editing the rule.", ephemeral=True)
    
    async def cancel_edit(self, interaction: discord.Interaction):
        """Cancel rule editing"""
        embed = discord.Embed(
            title="❌ Edit Cancelled",
            description="No changes were made to the autoresponder rule.",
            color=discord.Color.red()
        )
        
        # Disable all buttons
        self.toggle_button.disabled = True
        for item in self.children:
            if isinstance(item, discord.ui.Button):
                item.disabled = True
        
        await interaction.response.edit_message(embed=embed, view=self)


# Export the command group and help command
__all__ = ['autoresponder_group', 'autoresponder_help']
