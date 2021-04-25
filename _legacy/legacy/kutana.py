import json
import kutana


# Import configuration
with open("config.json") as fh:
    config = json.load(fh)

# Create application
app = kutana.Kutana()

# Add manager to application
app.add_backend(kutana.backends.Vkontakte(token=config["vk_token"]))

# Load and register plugins
app.add_plugins(kutana.load_plugins("plugins/"))

if __name__ == "__main__":
    # Run application
    app.run()