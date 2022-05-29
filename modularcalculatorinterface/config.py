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
            self.locations.append((PosixPath(os.environ['XDG_CONFIG_HOME'], self.config_dir_name), True))
        else:
            self.locations.append((PosixPath(os.environ['HOME'], '.config', self.config_dir_name), True))
        if 'XDG_CONFIG_DIRS' in os.environ:
            self.locations.extend([(PosixPath(d, self.config_dir_name), True) for d in os.environ['XDG_CONFIG_DIRS'].split(':')])
        self.locations.append((PosixPath('/etc', self.config_dir_name), True))
        self.locations.append((PosixPath('/app', 'share', self.config_dir_name), False))
        self.locations.append((PosixPath('/usr', 'share', self.config_dir_name), False))
        self.locations.append((PosixPath(initDir.parent, 'config', self.config_dir_name), False))

        # Load config
        self.loadMainConfig()
        self.loadThemes()
        self.loadVersion()

    def find(self, glob, allowUser=True, allowSystem=True, mergeAll=False):
        found = {}
        for location, isUser in self.locations:
            if isUser and not allowUser:
                continue
            if not isUser and not allowSystem:
                continue
            for f in location.glob(glob):
                file_id = f.relative_to(location)
                if mergeAll:
                    if not file_id in found:
                        found[file_id] = [f]
                    else:
                        found[file_id].append(f)
                elif not file_id in found:
                    found[file_id] = f
        return found

    def load(self, glob, allowUser=True, allowSystem=True, mergeAll=False):
        found = self.find(glob, allowUser, allowSystem, mergeAll)
        loaded = {}
        for file_id, file_path in found.items():
            if mergeAll:
                if file_id not in loaded:
                    loaded[file_id] = {}
                for f in file_path:
                    with open(f, 'r') as fh:
                        this_file = yaml.load(fh, Loader=yaml.CLoader)
                        if this_file is not None:
                            for top_level_id, top_level in this_file.items():
                                if top_level_id not in loaded[file_id]:
                                    loaded[file_id][top_level_id] = {}
                                if top_level is not None:
                                    for second_level_id, second_level in top_level.items():
                                        if second_level_id not in loaded[file_id][top_level_id] and second_level is not None:
                                            loaded[file_id][top_level_id][second_level_id] = second_level
            else:
                with open(file_path, 'r') as fh:
                    loaded[file_id] = yaml.load(fh, Loader=yaml.CLoader)
        return loaded

    def loadMainConfig(self):
        main = self.load('config.yml', mergeAll=True)
        if len(main.keys()) > 0:
            self.main = list(main.values())[0]
        else:
            self.main = None

    def saveMainConfig(self):
        found = self.find('config.yml', allowSystem=False)
        if len(found) > 0:
            try:
                self.writeMainConfig(list(found.values())[0])
                return
            except IOError:
                pass
        location = [l[0] for l in self.locations if l[1]][0]
        self.writeMainConfig(PosixPath(location, 'config.yml'))

    def writeMainConfig(self, file_path):
        if not file_path.parent.exists():
            file_path.parent.mkdir(mode=0o755, parents=True)
        with open(file_path, 'w') as fh:
            yaml.dump(self.main, fh)


    def loadThemes(self):
        self.themes = self.load('themes/*.yml')

    def loadVersion(self):
        self.version = list(self.load('version.yml', allowUser=False).values())[0]
