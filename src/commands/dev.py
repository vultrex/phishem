"""
Development commands for debugging and testing
"""
# pyright: reportAttributeAccessIssue=false, reportUnknownMemberType=false, reportMissingTypeStubs=false, reportGeneralTypeIssues=false
import aiohttp
import asyncio
import discord
from typing import Any
import gc
import logging
import os
import psutil
import sys
import time
import traceback
from collections import defaultdict, deque
from datetime import datetime, timedelta, timezone
from discord import app_commands

logger = logging.getLogger(__name__)

# Global error tracking
error_tracker = defaultdict(lambda: deque(maxlen=50))
last_errors = deque(maxlen=20)

# Dev override state
dev_override_enabled = False


def track_error(error_type: str, error: Exception):
    """Track errors for monitoring"""
    error_info = {
        'timestamp': datetime.now(timezone.utc),
        'type': error_type,
        'message': str(error),
        'traceback': traceback.format_exc()
    }
    error_tracker[error_type].append(error_info)
    last_errors.append(error_info)


def is_dev_user(user_id: int) -> bool:
    """Check if user is the designated developer"""
    dev_user_id = os.getenv('DEV')
    return bool(dev_user_id and str(user_id) == dev_user_id)


def has_dev_override(user_id: int) -> bool:
    """Check if dev override is enabled for the developer"""
    return is_dev_user(user_id) and dev_override_enabled


def get_dev_override_status() -> bool:
    """Get current dev override status"""
    return dev_override_enabled


def set_dev_override_status(enabled: bool) -> bool:
    """Set dev override status"""
    global dev_override_enabled
    dev_override_enabled = enabled
    return dev_override_enabled


# Developer command group
dev_group = app_commands.Group(name="dev", description="Developer commands")


@dev_group.command(name="panel", description="Open the developer control panel")
async def dev_panel(interaction: discord.Interaction):
    """Show the interactive developer panel"""
    if not is_dev_user(interaction.user.id):
        await interaction.response.send_message("❌ This command is restricted to developers.", ephemeral=True)
        return

    try:
        # Create the developer panel view
        view = DevPanelView()
        
        # Create main panel embed
        embed = discord.Embed(
            title="🔧 Developer Control Panel",
            description="Advanced debugging and monitoring tools:",
            color=discord.Color.blue()
        )
        
        # Show dev override status
        override_status = get_dev_override_status()
        override_status_text = "🔓 **ENABLED**" if override_status else "🔒 **DISABLED**"
        embed.add_field(
            name="🚨 Dev Override Status",
            value=f"Permission Bypass: {override_status_text}",
            inline=False
        )
        
        embed.add_field(
            name="ℹ️ Usage",
            value="Use the buttons below to access various debugging and monitoring tools.\n"
                  "All actions are developer-only and logged for security.",
            inline=False
        )
        
        embed.timestamp = datetime.now(timezone.utc)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=False)
        
    except Exception as e:
        logger.error(f"Error creating dev panel: {e}")
        await interaction.response.send_message(f"❌ Error creating dev panel: {str(e)}", ephemeral=True)


class DevPanelView(discord.ui.View):
    """Interactive developer panel with buttons"""

    def __init__(self):
        super().__init__(timeout=300)  # 5 minute timeout
        # Initial override button styling will be handled on first toggle; default decorator label used.

    @discord.ui.button(label="🔄 Reload Engine", style=discord.ButtonStyle.primary, row=0)
    async def reload_engine_button(self, interaction: discord.Interaction, button: Any):
        """Reload the anti-phishing engine"""
        if not is_dev_user(interaction.user.id):
            await interaction.response.send_message("❌ This action is restricted to developers.", ephemeral=True)
            return

        try:
            await interaction.response.defer(ephemeral=True)

            from src.optimizations import optimized_engine

            # Cleanup and reinitialize
            await optimized_engine.cleanup()
            await optimized_engine.initialize()

            await interaction.followup.send("✅ Anti-phishing engine reloaded successfully.", ephemeral=True)

        except Exception as e:
            logger.error(f"Error reloading engine: {e}")
            await interaction.followup.send(f"❌ Error reloading engine: {str(e)}", ephemeral=True)

    @discord.ui.button(label="🔄 Sync Commands", style=discord.ButtonStyle.success, row=0)
    async def sync_commands_button(self, interaction: discord.Interaction, button: Any):
        """Sync slash commands to Discord"""
        if not is_dev_user(interaction.user.id):
            await interaction.response.send_message("❌ This action is restricted to developers.", ephemeral=True)
            return

        try:
            await interaction.response.defer(ephemeral=True)

            synced = await interaction.client.tree.sync()  # type: ignore
            await interaction.followup.send(f"✅ Synced {len(synced)} commands successfully.", ephemeral=True)

        except Exception as e:
            logger.error(f"Error syncing commands: {e}")
            await interaction.followup.send(f"❌ Error syncing commands: {str(e)}", ephemeral=True)

    @discord.ui.button(label="📋 Guild Info", style=discord.ButtonStyle.secondary, row=0)
    async def list_guilds_button(self, interaction: discord.Interaction, button: Any):
        """List all guilds the bot is connected to"""
        if not is_dev_user(interaction.user.id):
            await interaction.response.send_message("❌ This action is restricted to developers.", ephemeral=True)
            return

        try:
            guilds = interaction.client.guilds

            embed = discord.Embed(
                title=f"📋 Connected Guilds ({len(guilds)})",
                color=discord.Color.blue()
            )

            guild_info = []
            for guild in guilds[:10]:  # Limit to first 10
                member_count = guild.member_count or 0
                guild_info.append(f"**{guild.name}** (ID: {guild.id})\nMembers: {member_count}")

            if guild_info:
                embed.description = "\n\n".join(guild_info)
            else:
                embed.description = "No guilds found."

            if len(guilds) > 10:
                embed.set_footer(text=f"Showing first 10 of {len(guilds)} guilds")

            await interaction.response.send_message(embed=embed, ephemeral=True)

        except Exception as e:
            logger.error(f"Error listing guilds: {e}")
            await interaction.response.send_message(f"❌ Error listing guilds: {str(e)}", ephemeral=True)

    @discord.ui.button(label="📊 System Stats", style=discord.ButtonStyle.secondary, row=0)
    async def system_stats_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Show detailed system and bot statistics"""
        if not is_dev_user(interaction.user.id):
            await interaction.response.send_message("❌ This action is restricted to developers.", ephemeral=True)
            return

        try:
            await interaction.response.defer(ephemeral=True)

            bot = interaction.client
            process = psutil.Process()

            # Bot stats
            guilds = len(bot.guilds)
            total_members = sum(guild.member_count or 0 for guild in bot.guilds)

            # System stats
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            bot_memory = process.memory_info().rss / 1024 / 1024  # MB

            # Bot uptime
            uptime = timedelta(seconds=int(time.time() - process.create_time()))

            embed = discord.Embed(
                title="📊 System & Bot Statistics",
                color=discord.Color.green()
            )

            embed.add_field(
                name="🤖 Bot Stats",
                value=f"Guilds: **{guilds:,}**\n"
                      f"Total Members: **{total_members:,}**\n"
                      f"Latency: **{bot.latency * 1000:.1f}ms**\n"
                      f"Uptime: **{uptime}**",
                inline=True
            )

            embed.add_field(
                name="💻 System Stats",
                value=f"CPU Usage: **{cpu_percent:.1f}%**\n"
                      f"RAM Usage: **{memory.percent:.1f}%**\n"
                      f"Bot Memory: **{bot_memory:.1f} MB**\n"
                      f"Python: **{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}**",
                inline=True
            )

            embed.add_field(
                name="📈 Memory Details",
                value=f"Total RAM: **{memory.total / 1024 ** 3:.1f} GB**\n"
                      f"Available: **{memory.available / 1024 ** 3:.1f} GB**\n"
                      f"Used: **{memory.used / 1024 ** 3:.1f} GB**",
                inline=True
            )

            embed.timestamp = datetime.now(timezone.utc)

            await interaction.followup.send(embed=embed, ephemeral=True)

        except Exception as e:
            logger.error(f"Error getting system stats: {e}")
            await interaction.followup.send(f"❌ Error getting system stats: {str(e)}", ephemeral=True)

    @discord.ui.button(label="🗃️ Cache Info", style=discord.ButtonStyle.secondary, row=1)
    async def cache_info_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Show cache statistics and information"""
        if not is_dev_user(interaction.user.id):
            await interaction.response.send_message("❌ This action is restricted to developers.", ephemeral=True)
            return

        try:
            await interaction.response.defer(ephemeral=True)

            embed = discord.Embed(
                title="🗃️ Cache Information",
                color=discord.Color.orange()
            )

            # Discord.py cache stats
            bot = interaction.client
            embed.add_field(
                name="📦 Discord Cache",
                value=f"Guilds: **{len(bot.guilds)}**\n"
                      f"Users: **{len(bot.users)}**\n"
                      f"Channels: **{len([c for c in bot.get_all_channels()])}**\n"
                      f"Emojis: **{len(bot.emojis)}**",
                inline=True
            )

            # Try to get anti-phishing cache stats
            try:
                from src.optimizations import optimized_engine
                # Use stats attribute if available
                if hasattr(optimized_engine, 'stats'):
                    cache_stats = optimized_engine.stats
                    embed.add_field(
                        name="🛡️ Anti-Phishing Cache",
                        value=f"Operations: **{len(cache_stats)}**\n"
                              f"Stats Available: **Yes**",
                        inline=True
                    )
                else:
                    embed.add_field(
                        name="🛡️ Anti-Phishing Cache",
                        value="Cache stats not available",
                        inline=True
                    )
            except ImportError:
                embed.add_field(
                    name="🛡️ Anti-Phishing Cache",
                    value="Optimized engine not loaded",
                    inline=True
                )

            embed.timestamp = datetime.now(timezone.utc)
            await interaction.followup.send(embed=embed, ephemeral=True)

        except Exception as e:
            logger.error(f"Error getting cache info: {e}")
            await interaction.followup.send(f"❌ Error getting cache info: {str(e)}", ephemeral=True)

    @discord.ui.button(label="🧹 Clear Cache", style=discord.ButtonStyle.danger, row=1)
    async def clear_cache_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Clear various caches"""
        if not is_dev_user(interaction.user.id):
            await interaction.response.send_message("❌ This action is restricted to developers.", ephemeral=True)
            return

        try:
            await interaction.response.defer(ephemeral=True)

            cleared = []

            # Clear anti-phishing cache
            try:
                from src.optimizations import optimized_engine
                if hasattr(optimized_engine, 'cleanup') and hasattr(optimized_engine, 'initialize'):
                    await optimized_engine.cleanup()
                    await optimized_engine.initialize()
                    cleared.append("Anti-phishing engine (restarted)")
            except (ImportError, AttributeError):
                pass

            # Clear user attempts cache
            try:
                from src.features.user_attempts import user_attempt_tracker
                # Reset attempts for all tracked users (simplified approach)
                user_attempt_tracker.cleanup_expired()
                cleared.append("User attempts cache (cleaned up)")
            except (ImportError, AttributeError):
                pass

            if cleared:
                await interaction.followup.send(f"✅ Cleared: {', '.join(cleared)}", ephemeral=True)
            else:
                await interaction.followup.send("⚠️ No caches were cleared (none available)", ephemeral=True)

        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            await interaction.followup.send(f"❌ Error clearing cache: {str(e)}", ephemeral=True)

    @discord.ui.button(label="📝 Recent Logs", style=discord.ButtonStyle.secondary, row=1)
    async def recent_logs_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Show recent log entries"""
        if not is_dev_user(interaction.user.id):
            await interaction.response.send_message("❌ This action is restricted to developers.", ephemeral=True)
            return

        try:
            await interaction.response.defer(ephemeral=True)

            # Get recent log entries from memory (if available)
            embed = discord.Embed(
                title="📝 Recent Log Activity",
                description="Last 10 log entries from various loggers:",
                color=discord.Color.purple()
            )

            # Try to get recent logs from different modules
            log_sources = [
                ("optimizations", "Anti-phishing engine"),
                ("events.message", "Message handler"),
                ("commands", "Commands"),
                ("main", "Main bot")
            ]

            for module_name, description in log_sources:
                try:
                    module_logger = logging.getLogger(module_name)
                    # Note: This is basic - in production you'd want a proper log handler
                    embed.add_field(
                        name=f"📊 {description}",
                        value=f"Logger: `{module_name}`\nLevel: {logging.getLevelName(module_logger.level)}",
                        inline=True
                    )
                except Exception:
                    continue

            embed.add_field(
                name="ℹ️ Note",
                value="For detailed logs, check the console output or log files.",
                inline=False
            )

            embed.timestamp = datetime.now(timezone.utc)
            await interaction.followup.send(embed=embed, ephemeral=True)

        except Exception as e:
            logger.error(f"Error getting recent logs: {e}")
            await interaction.followup.send(f"❌ Error getting recent logs: {str(e)}", ephemeral=True)

    @discord.ui.button(label="🔍 Test URL", style=discord.ButtonStyle.secondary, row=1)
    async def test_url_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Test a URL against the anti-phishing engine"""
        if not is_dev_user(interaction.user.id):
            await interaction.response.send_message("❌ This action is restricted to developers.", ephemeral=True)
            return

        await interaction.response.send_message("❌ TestURLModal is not implemented.", ephemeral=True)

    @discord.ui.button(label="⚡ Performance", style=discord.ButtonStyle.secondary, row=2)
    async def performance_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Show performance metrics"""
        if not is_dev_user(interaction.user.id):
            await interaction.response.send_message("❌ This action is restricted to developers.", ephemeral=True)
            return

        try:
            await interaction.response.defer(ephemeral=True)

            embed = discord.Embed(
                title="⚡ Performance Metrics",
                color=discord.Color.gold()
            )

            # Try to get performance data
            try:
                from src.optimizations.performance import performance_monitor
                perf_stats = performance_monitor.get_stats()
                # Example: show total uptime and operation count
                embed.add_field(
                    name="� Analysis Times",
                    value=f"Uptime: **{perf_stats.get('uptime_seconds', 'N/A'):.0f}s**\n"
                          f"Tracked Operations: **{len(perf_stats.get('operations', {}))}**",
                    inline=True
                )
            except (ImportError, AttributeError):
                embed.add_field(
                    name="⚠️ Performance Module",
                    value="Performance tracking not available",
                    inline=False
                )

            embed.timestamp = datetime.now(timezone.utc)
            await interaction.followup.send(embed=embed, ephemeral=True)

        except Exception as e:
            logger.error(f"Error getting performance metrics: {e}")
            await interaction.followup.send(f"❌ Error getting performance metrics: {str(e)}", ephemeral=True)

    @discord.ui.button(label="🔧 Database Info", style=discord.ButtonStyle.secondary, row=2)
    async def database_info_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Show database information"""
        if not is_dev_user(interaction.user.id):
            await interaction.response.send_message("❌ This action is restricted to developers.", ephemeral=True)
            return

        try:
            await interaction.response.defer(ephemeral=True)

            embed = discord.Embed(
                title="🔧 Database Information",
                color=discord.Color.teal()
            )

            # Guild config database
            try:
                import sqlite3
                conn = sqlite3.connect('guild_config.db')
                cursor = conn.cursor()

                cursor.execute("SELECT COUNT(*) FROM guild_config")
                guild_count = cursor.fetchone()[0]

                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = cursor.fetchall()

                embed.add_field(
                    name="📁 Guild Config DB",
                    value=f"Configured Guilds: **{guild_count}**\n"
                          f"Tables: **{len(tables)}**",
                    inline=True
                )

                conn.close()
            except Exception as e:
                embed.add_field(
                    name="📁 Guild Config DB",
                    value=f"Error: {str(e)[:50]}...",
                    inline=True
                )

            # User attempts database (if exists)
            try:
                from src.features.user_attempts import get_attempt_stats
                user_stats = get_attempt_stats()
                embed.add_field(
                    name="👥 User Attempts",
                    value=f"Total Guilds: **{user_stats.get('total_guilds', 'N/A')}**\n"
                          f"Total Users: **{user_stats.get('total_users', 'N/A')}**",
                    inline=True
                )
            except ImportError:
                embed.add_field(
                    name="👥 User Attempts",
                    value="Module not available",
                    inline=True
                )

            embed.timestamp = datetime.now(timezone.utc)
            await interaction.followup.send(embed=embed, ephemeral=True)

        except Exception as e:
            logger.error(f"Error getting database info: {e}")
            await interaction.followup.send(f"❌ Error getting database info: {str(e)}", ephemeral=True)

    @discord.ui.button(label="🔄 Refresh Panel", style=discord.ButtonStyle.primary, row=2)
    async def refresh_panel_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Refresh the dev panel"""
        if not is_dev_user(interaction.user.id):
            await interaction.response.send_message("❌ This action is restricted to developers.", ephemeral=True)
            return

        # Get current override status (simplified approach)
        override_status = get_dev_override_status()

        embed = discord.Embed(
            title="🔧 Developer Control Panel",
            description="Enhanced debugging and monitoring tools:",
            color=discord.Color.blue()
        )

        # Show dev override status
        override_status_text = "🔓 **ENABLED**" if override_status else "🔒 **DISABLED**"
        embed.add_field(
            name="� Dev Override Status",
            value=f"Permission Bypass: {override_status_text}",
            inline=False
        )

        embed.add_field(
            name="�🔄 Core Actions",
            value="🔄 **Reload Engine** - Restart anti-phishing engine\n"
                  "🔄 **Sync Commands** - Sync slash commands\n"
                  "📋 **Guild Info** - Show connected servers\n"
                  "📊 **System Stats** - Detailed system metrics\n"
                  f"{'🔓 **Override ON**' if override_status else '🔒 **Override OFF**'} - Toggle permission bypass",
            inline=False
        )

        embed.add_field(
            name="🔍 Analysis & Debug",
            value="🗃️ **Cache Info** - View cache statistics\n"
                  "🧹 **Clear Cache** - Clear various caches\n"
                  "📝 **Recent Logs** - Show recent log activity\n"
                  "🔍 **Test URL** - Test URLs against engine\n"
                  "🚨 **Error Monitor** - View error statistics\n"
                  "🧠 **Memory Monitor** - Memory usage & leaks\n"
                  "📝 **Console Logs** - Manage log levels",
            inline=False
        )

        embed.add_field(
            name="📊 Monitoring & Analysis",
            value="⚡ **Performance** - Performance metrics\n"
                  "🔧 **Database Info** - Database statistics\n"
                  "🌐 **Network Test** - Check connectivity\n"
                  "⚙️ **Bot Config** - Configuration details\n"
                  "🔬 **System Analysis** - Advanced diagnostics",
            inline=False
        )

        view = DevPanelView()
        await interaction.response.edit_message(embed=embed, view=view)

    @discord.ui.button(label="🌐 Network Test", style=discord.ButtonStyle.secondary, row=3)
    async def network_test_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Test network connectivity and Discord API status"""
        if not is_dev_user(interaction.user.id):
            await interaction.response.send_message("❌ This action is restricted to developers.", ephemeral=True)
            return

        try:
            await interaction.response.defer(ephemeral=True)
            
            embed = discord.Embed(
                title="🌐 Network & API Status",
                color=discord.Color.blue()
            )

            # Test Discord API latency
            bot_latency = interaction.client.latency * 1000
            
            # Test external URLs
            test_urls = [
                ("Discord API", "https://discord.com/api/v10/gateway"),
                ("GitHub", "https://api.github.com"),
                ("AdGuard Filters", "https://adguardteam.github.io/HostlistsRegistry/assets/filter_9.txt")
            ]
            
            connectivity_results = []
            
            for name, url in test_urls:
                try:
                    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
                        start_time = time.time()
                        async with session.get(url) as response:
                            response_time = (time.time() - start_time) * 1000
                            status = "✅" if response.status == 200 else f"⚠️ {response.status}"
                            connectivity_results.append(f"{status} **{name}**: {response_time:.1f}ms")
                except Exception as e:
                    connectivity_results.append(f"❌ **{name}**: {str(e)[:30]}")

            embed.add_field(
                name="🤖 Discord Bot",
                value=f"Latency: **{bot_latency:.1f}ms**\n"
                      f"Status: **{'🟢 Online' if interaction.client.is_ready() else '🔴 Offline'}**",
                inline=False
            )
            
            embed.add_field(
                name="🌍 External Services",
                value="\n".join(connectivity_results),
                inline=False
            )

            await interaction.followup.send(embed=embed, ephemeral=True)

        except Exception as e:
            logger.error(f"Error in network test: {e}")
            await interaction.followup.send(f"❌ Network test failed: {str(e)}", ephemeral=True)

    @discord.ui.button(label="🚨 Error Monitor", style=discord.ButtonStyle.danger, row=3)
    async def error_monitor_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """View recent errors and error statistics"""
        if not is_dev_user(interaction.user.id):
            await interaction.response.send_message("❌ This action is restricted to developers.", ephemeral=True)
            return

        try:
            await interaction.response.defer(ephemeral=True)
            
            embed = discord.Embed(
                title="🚨 Error Monitor",
                description="Recent errors and statistics:",
                color=discord.Color.red()
            )

            # Show recent errors from our global tracker
            if last_errors:
                recent_error_text = []
                for error in list(last_errors)[-5:]:  # Last 5 errors
                    timestamp = error['timestamp'].strftime('%H:%M:%S')
                    error_type = error['type']
                    message = error['message'][:50] + "..." if len(error['message']) > 50 else error['message']
                    recent_error_text.append(f"`{timestamp}` **{error_type}**: {message}")
                
                embed.add_field(
                    name="🕐 Recent Errors (Last 5)",
                    value="\n".join(recent_error_text) if recent_error_text else "No recent errors",
                    inline=False
                )
            else:
                embed.add_field(
                    name="🕐 Recent Errors",
                    value="No errors tracked",
                    inline=False
                )

            # Error statistics by type
            error_stats = {}
            for error_type, errors in error_tracker.items():
                error_stats[error_type] = len(errors)
            
            if error_stats:
                stats_text = []
                for error_type, count in sorted(error_stats.items(), key=lambda x: x[1], reverse=True)[:10]:
                    stats_text.append(f"**{error_type}**: {count}")
                
                embed.add_field(
                    name="📊 Error Types (Top 10)",
                    value="\n".join(stats_text),
                    inline=False
                )

            embed.timestamp = datetime.now(timezone.utc)
            await interaction.followup.send(embed=embed, ephemeral=True)

        except Exception as e:
            logger.error(f"Error in error monitor: {e}")
            await interaction.followup.send(f"❌ Error monitor failed: {str(e)}", ephemeral=True)

    @discord.ui.button(label="🧠 Memory Monitor", style=discord.ButtonStyle.secondary, row=3)
    async def memory_monitor_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Advanced memory usage monitoring and leak detection"""
        if not is_dev_user(interaction.user.id):
            await interaction.response.send_message("❌ This action is restricted to developers.", ephemeral=True)
            return

        try:
            await interaction.response.defer(ephemeral=True)
            
            embed = discord.Embed(
                title="🧠 Memory Monitor",
                description="Advanced memory analysis and garbage collection:",
                color=discord.Color.purple()
            )

            # Memory stats
            process = psutil.Process()
            memory_info = process.memory_info()
            memory_percent = process.memory_percent()
            
            # Garbage collection stats
            gc_stats = gc.get_stats()
            gc_counts = gc.get_count()
            
            # Force garbage collection and see what's collected
            collected = gc.collect()

            embed.add_field(
                name="💾 Process Memory",
                value=f"RSS: **{memory_info.rss / 1024 / 1024:.1f} MB**\n"
                      f"VMS: **{memory_info.vms / 1024 / 1024:.1f} MB**\n"
                      f"Percent: **{memory_percent:.1f}%**",
                inline=True
            )

            embed.add_field(
                name="🗑️ Garbage Collection",
                value=f"Gen 0: **{gc_counts[0]}** objects\n"
                      f"Gen 1: **{gc_counts[1]}** objects\n"
                      f"Gen 2: **{gc_counts[2]}** objects\n"
                      f"Collected: **{collected}** objects",
                inline=True
            )

            # Discord.py cache stats
            bot = interaction.client
            embed.add_field(
                name="🤖 Discord Cache",
                value=f"Guilds: **{len(bot.guilds)}**\n"
                      f"Users: **{len(bot.users)}**\n"
                      f"Channels: **{sum(len(guild.channels) for guild in bot.guilds)}**\n"
                      f"Messages: **{len(bot.cached_messages)}**",
                inline=True
            )

            # Try to get custom cache info
            try:
                # Check if we have cache stats available
                cache_info = []
                try:
                    # Generic fallback for cache info
                    cache_info.append("Basic cache monitoring available")
                except Exception:
                    cache_info.append("Cache manager not available")
                
                embed.add_field(
                    name="🗃️ Custom Caches", 
                    value="\n".join(cache_info) if cache_info else "No custom caches",
                    inline=False
                )
            except Exception:
                embed.add_field(
                    name="🗃️ Custom Caches",
                    value="Cache module not available",
                    inline=False
                )

            embed.timestamp = datetime.now(timezone.utc)
            await interaction.followup.send(embed=embed, ephemeral=True)

        except Exception as e:
            logger.error(f"Error in memory monitor: {e}")
            await interaction.followup.send(f"❌ Memory monitor failed: {str(e)}", ephemeral=True)

    @discord.ui.button(label="⚙️ Bot Config", style=discord.ButtonStyle.secondary, row=4)
    async def bot_config_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Show bot configuration and environment variables"""
        if not is_dev_user(interaction.user.id):
            await interaction.response.send_message("❌ This action is restricted to developers.", ephemeral=True)
            return

        try:
            await interaction.response.defer(ephemeral=True)
            
            embed = discord.Embed(
                title="⚙️ Bot Configuration",
                description="Current configuration and environment:",
                color=discord.Color.gold()
            )

            # Bot configuration
            try:
                from src.core.config import config
                embed.add_field(
                    name="🤖 Bot Settings",
                    value=f"Autoresponder: **{'✅' if config.AUTORESPONDER_ENABLED else '❌'}**\n"
                          f"Cooldown: **{config.AUTORESPONDER_COOLDOWN}s**\n"
                          f"Max Response Length: **{config.AUTORESPONDER_MAX_RESPONSE_LENGTH}**",
                    inline=True
                )
            except ImportError:
                embed.add_field(
                    name="🤖 Bot Settings",
                    value="Config module not available",
                    inline=True
                )

            # Environment info
            env_vars = ["BOT_TOKEN", "DEV", "DATABASE_URL", "REDIS_URL"]
            env_status = []
            for var in env_vars:
                value = os.getenv(var)
                if var == "BOT_TOKEN":
                    status = "✅ Set" if value else "❌ Missing"
                else:
                    status = f"✅ {value[:20]}..." if value else "❌ Not set"
                env_status.append(f"**{var}**: {status}")

            embed.add_field(
                name="🌍 Environment",
                value="\n".join(env_status),
                inline=True
            )

            # Python and system info
            embed.add_field(
                name="🐍 Runtime",
                value=f"Python: **{sys.version.split()[0]}**\n"
                      f"Platform: **{sys.platform}**\n"
                      f"Architecture: **{sys.maxsize > 2**32 and '64-bit' or '32-bit'}**",
                inline=True
            )

            # Discord.py version
            embed.add_field(
                name="📚 Libraries",
                value=f"Discord.py: **{discord.__version__}**\n"
                      f"Aiohttp: **{aiohttp.__version__}**\n"
                      f"PSUtil: **{psutil.__version__}**",
                inline=True
            )

            embed.timestamp = datetime.now(timezone.utc)
            await interaction.followup.send(embed=embed, ephemeral=True)

        except Exception as e:
            logger.error(f"Error in bot config: {e}")
            await interaction.followup.send(f"❌ Bot config failed: {str(e)}", ephemeral=True)

    @discord.ui.button(label="🔬 System Analysis", style=discord.ButtonStyle.secondary, row=4)
    async def system_analysis_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Advanced system diagnostics and analysis"""
        if not is_dev_user(interaction.user.id):
            await interaction.response.send_message("❌ This action is restricted to developers.", ephemeral=True)
            return

        try:
            await interaction.response.defer(ephemeral=True)
            
            embed = discord.Embed(
                title="🔬 System Analysis",
                description="Advanced system diagnostics:",
                color=discord.Color.dark_blue()
            )

            # CPU and load info
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            load_avg = psutil.getloadavg() if hasattr(psutil, 'getloadavg') else (0, 0, 0)
            
            embed.add_field(
                name="🖥️ CPU Analysis",
                value=f"Cores: **{cpu_count}**\n"
                      f"Frequency: **{cpu_freq.current:.0f} MHz**\n"
                      f"Load Avg: **{load_avg[0]:.2f}**",
                inline=True
            )

            # Disk usage
            disk_usage = psutil.disk_usage('/')
            embed.add_field(
                name="💽 Disk Usage",
                value=f"Total: **{disk_usage.total / 1024**3:.1f} GB**\n"
                      f"Used: **{disk_usage.used / 1024**3:.1f} GB**\n"
                      f"Free: **{disk_usage.free / 1024**3:.1f} GB**",
                inline=True
            )

            # Network stats
            net_io = psutil.net_io_counters()
            embed.add_field(
                name="🌐 Network I/O",
                value=f"Sent: **{net_io.bytes_sent / 1024**2:.1f} MB**\n"
                      f"Received: **{net_io.bytes_recv / 1024**2:.1f} MB**\n"
                      f"Packets: **{net_io.packets_sent + net_io.packets_recv}**",
                inline=True
            )

            # Process info
            process = psutil.Process()
            process_threads = process.num_threads()
            # File descriptors are Unix-only
            process_fds = 'N/A (Windows)' if sys.platform == 'win32' else 'Available on Unix'
            
            embed.add_field(
                name="🔧 Process Details",
                value=f"PID: **{process.pid}**\n"
                      f"Threads: **{process_threads}**\n"
                      f"File Descriptors: **{process_fds}**",
                inline=True
            )

            # Bot-specific analysis
            bot = interaction.client
            embed.add_field(
                name="🤖 Bot Analysis",
                value=f"Event Loop: **{'Running' if not bot.loop.is_closed() else 'Closed'}**\n"
                      f"Tasks: **{len([t for t in asyncio.all_tasks() if not t.done()])}**\n"
                      f"WebSocket: **{'Connected' if bot.ws else 'Disconnected'}**",
                inline=True
            )

            embed.timestamp = datetime.now(timezone.utc)
            await interaction.followup.send(embed=embed, ephemeral=True)

        except Exception as e:
            logger.error(f"Error in system analysis: {e}")
            await interaction.followup.send(f"❌ System analysis failed: {str(e)}", ephemeral=True)

    @discord.ui.button(label="📝 Console Logs", style=discord.ButtonStyle.secondary, row=4)
    async def console_logs_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Show recent console logs and manage log levels"""
        if not is_dev_user(interaction.user.id):
            await interaction.response.send_message("❌ This action is restricted to developers.", ephemeral=True)
            return

        try:
            await interaction.response.defer(ephemeral=True)

            embed = discord.Embed(
                title="📝 Console Log Manager",
                description="Recent logs and log level management:",
                color=discord.Color.blue()
            )

            # Show current log levels
            loggers_info = []
            
            # Get all active loggers
            active_loggers = [
                ("Root", logging.getLogger()),
                ("Discord", logging.getLogger("discord")),
                ("Bot Main", logging.getLogger("src.core.main")),
                ("Commands", logging.getLogger("src.commands")),
                ("Events", logging.getLogger("src.events")),
                ("Optimizations", logging.getLogger("src.optimizations")),
            ]
            
            for name, logger in active_loggers:
                level_name = logging.getLevelName(logger.level)
                loggers_info.append(f"**{name}**: {level_name}")
            
            embed.add_field(
                name="📊 Current Log Levels",
                value="\n".join(loggers_info),
                inline=False
            )

            # Show recent log entries from error tracker
            if last_errors:
                recent_logs = []
                for error in list(last_errors)[-5:]:  # Last 5 entries
                    timestamp = error['timestamp'].strftime('%H:%M:%S')
                    log_type = error['type']
                    message = error['message'][:40] + "..." if len(error['message']) > 40 else error['message']
                    recent_logs.append(f"`{timestamp}` **{log_type}**: {message}")
                
                embed.add_field(
                    name="🕐 Recent Log Entries",
                    value="\n".join(recent_logs) if recent_logs else "No recent entries",
                    inline=False
                )
            else:
                embed.add_field(
                    name="🕐 Recent Log Entries",
                    value="No recent log entries tracked",
                    inline=False
                )

            embed.add_field(
                name="💡 Log Level Management",
                value="Use the following commands to change log levels:\n"
                      "• `/dev panel` → Use this button → Manual log level changes\n"
                      "• **DEBUG**: Very detailed information\n"
                      "• **INFO**: General information\n"
                      "• **WARNING**: Warning messages\n"
                      "• **ERROR**: Error messages only\n"
                      "• **CRITICAL**: Critical errors only",
                inline=False
            )

            embed.timestamp = datetime.now(timezone.utc)
            await interaction.followup.send(embed=embed, ephemeral=True)

        except Exception as e:
            logger.error(f"Error in console logs: {e}")
            await interaction.followup.send(f"❌ Console logs failed: {str(e)}", ephemeral=True)

    @discord.ui.button(label="🔓 Dev Override", style=discord.ButtonStyle.danger, row=0)
    async def dev_override_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Toggle dev override mode to bypass permission checks"""
        if not is_dev_user(interaction.user.id):
            await interaction.response.send_message("❌ This action is restricted to developers.", ephemeral=True)
            return

        try:
            # Toggle the override status
            current_status = get_dev_override_status()
            new_status = set_dev_override_status(not current_status)
            
            # Update button appearance
            if new_status:
                button.style = discord.ButtonStyle.success
                button.label = "🔓 Override ON"
                status_text = "✅ **ENABLED**"
                description = "You can now bypass permission checks on bot commands."
                color = discord.Color.green()
            else:
                button.style = discord.ButtonStyle.danger
                button.label = "🔒 Override OFF"
                status_text = "❌ **DISABLED**"
                description = "Normal permission checks are now enforced."
                color = discord.Color.red()

            embed = discord.Embed(
                title="🔐 Developer Override Toggle",
                description=description,
                color=color
            )

            embed.add_field(
                name="🚨 Override Status",
                value=status_text,
                inline=True
            )

            embed.add_field(
                name="⚠️ Warning",
                value="Dev override bypasses **ALL** permission checks.\n"
                      "Use responsibly and disable when not needed.",
                inline=False
            )

            embed.add_field(
                name="📋 Affected Commands",
                value="• Settings commands (Manage Server)\n"
                      "• Autoresponder commands (Manage Messages)\n"
                      "• Moderation actions\n"
                      "• Any command with permission requirements",
                inline=False
            )

            # Update the view with the new button state
            await interaction.response.edit_message(embed=embed, view=self)

        except Exception as e:
            logger.error(f"Error toggling dev override: {e}")
            await interaction.response.send_message(f"❌ Error toggling dev override: {str(e)}", ephemeral=True)

    @discord.ui.button(label="🔐 Bot Permissions", style=discord.ButtonStyle.secondary, row=3)
    async def bot_permissions_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Check bot permissions for the current server"""
        if not is_dev_user(interaction.user.id):
            await interaction.response.send_message("❌ This action is restricted to developers.", ephemeral=True)
            return

        try:
            await interaction.response.defer(ephemeral=True)
            
            # Check if we're in a guild
            if not interaction.guild:
                await interaction.followup.send("❌ This command must be used in a server.", ephemeral=True)
                return
            
            guild = interaction.guild
            bot_member = guild.me
            
            if not bot_member:
                await interaction.followup.send("❌ Could not find bot member in this server.", ephemeral=True)
                return
            
            embed = discord.Embed(
                title="🔐 Bot Permissions Analysis",
                description=f"Checking bot permissions for **{guild.name}**:",
                color=discord.Color.blue()
            )

            # Required permissions for full functionality
            required_perms = {
                'manage_messages': 'Delete malicious messages',
                'moderate_members': 'Timeout users', 
                'kick_members': 'Kick users',
                'ban_members': 'Ban users',
                'send_messages': 'Send responses',
                'embed_links': 'Send rich embeds',
                'read_message_history': 'Read message content',
                'use_application_commands': 'Slash commands',
                'view_channel': 'View channels',
                'read_messages': 'Read messages',
                'send_messages_in_threads': 'Send messages in threads',
                'manage_threads': 'Manage threads',
                'use_external_emojis': 'Use external emojis'
            }

            permissions = bot_member.guild_permissions
            permission_status = []
            missing_count = 0
            
            # Check each required permission
            for perm_name, description in required_perms.items():
                has_perm = getattr(permissions, perm_name, False)
                status_icon = "✅" if has_perm else "❌"
                if not has_perm:
                    missing_count += 1
                
                perm_display = perm_name.replace('_', ' ').title()
                permission_status.append(f"{status_icon} **{perm_display}** - {description}")

            # Summary
            total_perms = len(required_perms)
            granted_perms = total_perms - missing_count
            
            if missing_count == 0:
                summary_color = "🟢"
                summary_text = "All permissions granted!"
            elif missing_count <= 2:
                summary_color = "🟡"
                summary_text = "Minor permissions missing"
            else:
                summary_color = "🔴"
                summary_text = "Critical permissions missing"
            
            embed.add_field(
                name="📊 Summary",
                value=f"{summary_color} **Status:** {summary_text}\n"
                      f"**Granted:** {granted_perms}/{total_perms} permissions\n"
                      f"**Missing:** {missing_count} permissions\n"
                      f"**Server:** {guild.name} ({guild.member_count} members)",
                inline=False
            )

            # Split permissions into two columns for better readability
            mid_point = len(permission_status) // 2
            first_half = permission_status[:mid_point]
            second_half = permission_status[mid_point:]
            
            embed.add_field(
                name="🔑 Core Permissions",
                value="\n".join(first_half),
                inline=True
            )
            
            embed.add_field(
                name="🔑 Additional Permissions", 
                value="\n".join(second_half),
                inline=True
            )

            # Add help text if there are missing permissions
            if missing_count > 0:
                embed.add_field(
                    name="💡 How to Fix Missing Permissions",
                    value="**Method 1 - Server Settings:**\n"
                          "1. Go to Server Settings > Roles\n"
                          "2. Find the bot's role or @everyone\n"
                          "3. Grant the missing permissions\n\n"
                          "**Method 2 - Re-invite Bot:**\n"
                          "1. Go to Discord Developer Portal\n"
                          "2. OAuth2 > URL Generator\n"
                          "3. Select 'bot' + 'applications.commands'\n"
                          "4. Select all required permissions\n"
                          "5. Use generated URL to re-invite",
                    inline=False
                )

            # Add administrator check
            if permissions.administrator:
                embed.add_field(
                    name="👑 Administrator",
                    value="✅ Bot has Administrator permissions (overrides all other permissions)",
                    inline=False
                )

            embed.timestamp = datetime.now(timezone.utc)
            await interaction.followup.send(embed=embed, ephemeral=True)

        except Exception as e:
            logger.error(f"Error checking bot permissions: {e}")
            await interaction.followup.send(f"❌ Permission check failed: {str(e)}", ephemeral=True)

    # (report-netcraft command moved to top-level below)

# Export the command group and dev override functions
__all__ = ['dev_group', 'is_dev_user', 'has_dev_override', 'get_dev_override_status', 'track_error']

# Top-level Netcraft report command (moved out of DevPanelView)
@dev_group.command(name="report-netcraft", description="Report one or more URLs to Netcraft for analysis")
@app_commands.describe(
    email="Your email address to receive the report",
    urls="One or more URLs to report (comma or space separated)",
    reason="Optional reason for reporting (up to 10,000 chars)",
    source="Optional source UUID if provided by Netcraft"
)
async def report_netcraft(interaction: discord.Interaction, email: str, urls: str, reason: str = "", source: str = ""):
    """Report URLs to Netcraft for analysis"""
    if not is_dev_user(interaction.user.id):
        await interaction.response.send_message("❌ This command is restricted to developers.", ephemeral=True)
        return

    await interaction.response.defer(ephemeral=True)

    # Parse URLs (comma or space separated)
    url_list = [u.strip() for u in urls.replace(',', ' ').split() if u.strip()]
    if not url_list:
        await interaction.followup.send("❌ No valid URLs provided.", ephemeral=True)
        return
    if len(url_list) > 1000:
        await interaction.followup.send("❌ Too many URLs (max 1000 per submission).", ephemeral=True)
        return

    payload = {"email": email, "urls": [{"url": u} for u in url_list]}
    if reason:
        payload["reason"] = reason[:10000]
    if source:
        payload["source"] = source

    netcraft_url = "https://report.netcraft.com/api/v1/report/url"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(netcraft_url, json=payload) as resp:
                resp_json = await resp.json()
                status = resp.status
                message = resp_json.get("message", "No message returned.")
                uuid = resp_json.get("uuid")

        embed = discord.Embed(
            title="Netcraft Report Submission",
            color=discord.Color.green() if status == 200 else discord.Color.red(),
            description=f"**Status:** {status}\n**Message:** {message}"
        )
        embed.add_field(name="URLs Reported", value=f"{len(url_list)} URL(s)", inline=True)
        embed.add_field(name="Email", value=email, inline=True)
        if uuid:
            embed.add_field(name="Submission UUID", value=f"`{uuid}`", inline=False)
            embed.set_footer(text="Use this UUID to monitor submission status.")
        if reason:
            embed.add_field(name="Reason", value=reason[:200] + ("..." if len(reason) > 200 else ""), inline=False)
        await interaction.followup.send(embed=embed, ephemeral=True)
    except Exception as e:
        logger.error(f"Error reporting to Netcraft: {e}")
        await interaction.followup.send(f"❌ Error reporting to Netcraft: {str(e)}", ephemeral=True)
