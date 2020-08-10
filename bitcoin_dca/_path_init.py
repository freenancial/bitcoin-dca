"""Setup `sys.path` for importing third party modules from git submodules.

Many third party modules assume their root direcotry paths are in `sys.path`.
For example, in `cbpro`, its `__init__.py` has imports like this:
    `from cbpro.cbpro_auth import CBProAuth`
If its root direcotry path isn't already in `sys.path`, assumptions like this
would cause module importing failure.

This module updates `sys.path` to add the root paths of all thiry party modules
added via git submodules. You should import this module before trying to
import any thiry party packages in git submodules.

Example usage:
    ```
    import _path_init  # pylint: disable=unused-import
    from coinbasepro_python import cbpro
    ```
"""
import sys
import os

sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.join(os.path.dirname(__file__), "coinbasepro_python"))
sys.path.append(os.path.join(os.path.dirname(__file__), "libpycoin"))
