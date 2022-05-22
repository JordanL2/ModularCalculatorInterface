#!/usr/bin/python3

from pathlib import PosixPath
import os
import yaml


class Config:

    def __init__(self, args):
        initDir = PosixPath(args[0]).parent

        # This is the name of the config dir, in any location
        self.config_dir_name = 'ModularCalculator'

        # Possible locations
        self.locations = []
        if 'XDG_CONFIG_HOME' in os.environ:
            self.locations.append(PosixPath(os.environ['XDG_CONFIG_HOME'], self.config_dir_name))
        else:
            self.locations.append(PosixPath(os.environ['HOME'], '.config', self.config_dir_name))
        if 'XDG_CONFIG_DIRS' in os.environ:
            self.locations.extend([PosixPath(d, self.config_dir_name) for d in os.environ['XDG_CONFIG_DIRS'].split(':')])
        self.locations.append(PosixPath('/etc', self.config_dir_name))
        self.locations.append(PosixPath('/app', 'share', self.config_dir_name))
        self.locations.append(PosixPath('/usr', 'share', self.config_dir_name))
        self.locations.append(PosixPath(initDir.parent, 'config', self.config_dir_name))

        # Filter for locations that exist
        self.locations = [l for l in self.locations if l.is_dir()]

        # Load config
        self.loadMainConfig()
        self.loadThemes()

    def load(self, glob):
        found = {}
        for location in self.locations:
            for f in location.glob(glob):
                file_id = f.relative_to(location)
                if not file_id in found:
                    with open(f, 'r') as fh:
                        found[file_id] = yaml.load(fh, Loader=yaml.CLoader)
        return found

    def loadMainConfig(self):
        main = self.load('config.yml')
        if len(main.keys()) > 0:
            self.main = list(main.values())[0]
        else:
            self.main = None

    def loadThemes(self):
        self.themes = self.load('themes/*.yml')
