# Home Digital Twin

A version-controlled smart home built on [Home Assistant](https://www.home-assistant.io/). This repo is the single source of truth for every automation, dashboard, integration, and configuration that runs the house.

## Why Home Assistant?

After years of bouncing between Homebridge, SmartThings, and bare MQTT setups, HA won because:

- **Huge device ecosystem** — 2,700+ integrations out of the box
- **Local-first** — runs on your own hardware, no cloud dependency
- **Automations as code** — YAML configs that live in git, not trapped in a vendor UI
- **Active community** — HACS, custom components, blueprints

## Project structure

```
home-digital-twin/
├── config/                  # Home Assistant configuration root (mounted into container)
│   ├── configuration.yaml   # Main HA config
│   ├── automations.yaml     # Automation definitions
│   ├── scripts.yaml         # Script definitions
│   ├── scenes.yaml          # Scene definitions
│   ├── secrets.yaml.example # Template for secrets (never commit the real one)
│   ├── automations/         # Split automation files (organized by room/function)
│   ├── scripts/             # Split script files
│   ├── scenes/              # Split scene files
│   ├── dashboards/          # Lovelace dashboard YAML
│   ├── packages/            # HA packages (bundled config per domain)
│   ├── custom_components/   # HACS / manual custom integrations
│   ├── blueprints/          # Reusable automation blueprints
│   └── www/                 # Static assets served by HA (icons, images)
├── docs/                    # Project documentation and scope
│   ├── runbooks/            # Step-by-step setup and ops (e.g. Z-Wave, backups)
├── docker-compose.yml       # Container orchestration
├── .env.example             # Environment variable template
└── .gitignore
```

## Quick start

### Prerequisites

- Docker and Docker Compose
- Git

### Setup

1. **Clone the repo**
   ```bash
   git clone https://github.com/timkelly86/home-digital-twin.git
   cd home-digital-twin
   ```

2. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your timezone, coordinates, etc.
   ```

3. **Set up secrets**
   ```bash
   cp config/secrets.yaml.example config/secrets.yaml
   # Edit config/secrets.yaml with your actual credentials
   ```

4. **Start Home Assistant**
   ```bash
   docker compose up -d
   ```

5. **Access the UI** at `http://<your-server-ip>:8123`

## Task walkthrough

**[docs/tasks-walkthrough.md](docs/tasks-walkthrough.md)** — Ordered checklist: what’s done, what’s next (Z-Wave devices, Lutron, dashboards, MyQ, pool, Tandem), with short steps and links to runbooks.

## Runbooks

Step-by-step guides for hardware and integrations:

- **[Z-Wave: Zooz 800 series stick](docs/runbooks/zwave-zooz-800-setup.md)** — Install Z-Wave JS, add the stick, and migrate locks/switches/sensors from Ring.

## Development workflow

All configuration changes go through git:

1. Edit config files locally or via the HA UI
2. Pull any UI-made changes back into the repo
3. Commit, push, review
4. Restart HA to pick up changes: `docker compose restart homeassistant`

## Roadmap

- [ ] Initial HA deployment and onboarding
- [ ] Device discovery and integration setup
- [ ] Room-by-room automation buildout
- [ ] Lovelace dashboards for each zone
- [ ] Energy monitoring
- [ ] Presence detection
- [ ] Nox integration (life admin command center)
- [ ] MQTT broker for custom IoT sensors

## Related

- [Nox (LifeAdmin)](https://github.com/timkelly86/) — the life automation app this feeds into

## License

Private — personal use only.
