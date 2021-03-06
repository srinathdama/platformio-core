# Copyright (c) 2014-present PlatformIO <contact@platformio.org>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import os

from platformio.package.exception import MissingPackageManifestError
from platformio.package.manager.base import BasePackageManager
from platformio.package.meta import PackageSpec, PackageType
from platformio.project.helpers import get_project_global_lib_dir


class LibraryPackageManager(BasePackageManager):  # pylint: disable=too-many-ancestors
    def __init__(self, package_dir=None):
        super(LibraryPackageManager, self).__init__(
            PackageType.LIBRARY, package_dir or get_project_global_lib_dir()
        )

    @property
    def manifest_names(self):
        return PackageType.get_manifest_map()[PackageType.LIBRARY]

    def find_pkg_root(self, path, spec):
        try:
            return super(LibraryPackageManager, self).find_pkg_root(path, spec)
        except MissingPackageManifestError:
            pass
        assert isinstance(spec, PackageSpec)

        root_dir = self.find_library_root(path)

        # automatically generate library manifest
        with open(os.path.join(root_dir, "library.json"), "w") as fp:
            json.dump(
                dict(name=spec.name, version=self.generate_rand_version(),),
                fp,
                indent=2,
            )

        return root_dir

    @staticmethod
    def find_library_root(path):
        for root, dirs, files in os.walk(path):
            if not files and len(dirs) == 1:
                continue
            for fname in files:
                if not fname.endswith((".c", ".cpp", ".h", ".S")):
                    continue
                if os.path.isdir(os.path.join(os.path.dirname(root), "src")):
                    return os.path.dirname(root)
                return root
        return path
