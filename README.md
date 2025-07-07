# Phishem

A Discord bot that helps protect your server from phishing links and malicious content. Built to be fast, reliable, and easy to use.

## What it does

- Scans messages for suspicious links in real-time
- Blocks known phishing domains automatically  
- Provides admin controls for managing protection settings
- Tracks and reports on blocked attempts
- Works quietly in the background without spam

## Getting started

### Prerequisites

- Python 3.11+
- A Discord bot token
- Docker (optional but recommended)

### Quick setup

1. Clone this repo
2. Copy `.env.example` to `.env` and add your bot token
3. Invite the bot to your server with admin permissions
4. Run it

### Running with Docker (recommended)

```bash
# Build and start
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

### Running locally

```bash
# Install dependencies
pip install -r requirements.txt

# Run the bot
python main.py
```

## Commands

- `/antiphish-stats` - View protection statistics
- `/settings` - Configure bot settings for your server
- `/help` - Show available commands

Most configuration is done through the `/settings` command with an interactive menu.

## Configuration

The bot uses a SQLite database to store per-server settings. Each server can configure:

- Anti-phishing protection (on/off)
- Autoresponder settings
- Action on detection (delete, warn, etc.)

## Performance

Built with performance in mind:
- Caches domain lists for fast lookups
- Optimized message scanning
- Low memory footprint
- Minimal API calls

## Contributing

Feel free to open issues or submit PRs. The code is organized into modules under `src/` for easier navigation.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---