from setuptools import setup, find_packages

setup(
    name="app_core_plugins",
    version="0.1.0",
    package_dir={"": "app"},
    packages=find_packages("app"),
    entry_points={
        "plugins": [
            "app_basic_auth = app.plugins.app_core.plugin:BasicAuthProviderPlugin",
        ],
    },
)