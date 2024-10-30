import traceback
import logging
from importlib.metadata import entry_points

from sqlalchemy.exc import SQLAlchemyError


from app.plugins import plugins, register

log = logging.getLogger(__name__)

def install_plugins():
    """
    INstall associated plugins
    """
    plugins = entry_points(group="plugins")
    log.info(f"Found plugins: {list(plugins)}")  # See if any plugins are found

    for ep in plugins:
        log.info(f"Loading plugin {ep}")
        try:
            plugin = ep.load()
            register(plugin)
            log.info(f"Loaded plugin {plugin}")
        except SQLAlchemyError:
            log.error(
                "Something went wrong with creating plugin rows, is the database setup correctly?"
            )
            log.error(f"Failed to load plugin {ep.name}:{traceback.format_exc()}")
        except KeyError as e:
            log.info(f"Failed to load plugin {ep.name} due to missing configuration items. {e}")
        except Exception:
            log.error(f"Failed to load plugin {ep.name}:{traceback.format_exc()}")
