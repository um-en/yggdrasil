import os
from yggdrasil.logger import logger
import yggdrasil.app
from yggdrasil.settings import Settings

# todo any way to nicely marry __subclass__ & code completion?
PATH_YGGDRASIL = os.environ.get("YGGDRASIL_ROOT", os.path.expanduser('~\Documents'))
_PATH_INTERNAL = os.path.join(os.path.dirname(__file__))


class AppManager(object):
    def __init__(self, apps: [], root: str):
        self.path_root = root
        self.path_settings = r'{0}\settings'.format(self.path_root)
        self.path_template_scripts = r'{0}\data'.format(_PATH_INTERNAL)
        self.path_scripts = r'{0}\scripts'.format(self.path_root)
        self.path_envs = r'{0}\venvs'.format(self.path_root)

        self.apps = apps
        # TODO Add log functionality (logging which app are installed etc...) + crash if log non resolvable

    @classmethod
    def _get_status(cls, root, app: str):
        # todo find better way (e.g. keeping an internal log of installed tools?)
        return os.path.exists(r'{0}\venvs\venv_{1}'.format(root, app))

    def show_apps(self):
        display_install = {
            True: 'Installed (@ {venv})',
            False: 'Not installed',
        }
        import pdb;pdb.set_trace()
        content = ['App {app_name} (type {type_app}) - Status: {status}'.format(
            app_name=app.name,
            type_app=app.__class__.identifier,
            status=display_install[app.is_installed].format(venv=app.venv_name))
            for app in self.apps]
        import pdb;pdb.set_trace()

        return '\n'.join(content)

    @classmethod
    def from_root(cls, root: str):
        settings = Settings.from_yaml(r"{0}\settings\settings.yaml".format(root), safe=True)
        apps = []
        class_apps = yggdrasil.app.Apps()
        for info_app in settings.base_types:
            class_app = class_apps.select(identifier=info_app['type'])
            class_app.set_class_constants(**info_app)
            for config in [config for config in settings.config_apps if config['type'] == class_app.identifier]:
                is_installed = cls._get_status(root, config['name'])
                apps.append(class_app(is_installed=is_installed, **config))
        return AppManager(apps=apps, root=root)

    @classmethod
    def seed_configs(cls, root):
        with open(r'{0}\data\template_settings.yaml'.format(_PATH_INTERNAL)) as f:
            batch_ls = f.readlines()
        with open(r'{0}\settings\settings.yaml'.format(root), 'w+') as f:
            f.write("".join(batch_ls))

    def _find_app(self, name):
        apps_match = [app for app in self.apps if app.name == name]
        if len(apps_match) == 0:
            raise Exception("App not found - Please check app name called")
        if len(apps_match) > 1:
            raise Exception("Several apps with this name - Please update base configuration")
        return apps_match[0]

    def create(self, app: str, **kwargs):
        _app = self._find_app(app)
        venv_match = [app for app in self.apps if app.venv_name == _app.venv_name and app.is_installed]
        _app.create(
            path_scripts=self.path_scripts,
            path_venvs=self.path_envs,
            path_templates=self.path_template_scripts,
            create_venv=len(venv_match) == 0, #TODO carry impact into functions
            **kwargs
        )
        # TODO Error handling if name isn't recorded in logs / settings

    def remove(self, app: str, **kwargs):
        _app = self._find_app(app)
        _app.remove(
            path_scripts=self.path_scripts,
            path_venvs=self.path_envs,
            path_templates=self.path_template_scripts,
            **kwargs
        )
        # TODO Error handling if name isn't recorded in logs / settings


if __name__ == "__main__":
    from pprint import pprint
    mger = AppManager.from_root(r"C:\Users\maxim\Documents\Yggdrasil")
    print(mger.show_apps())
    import pdb; pdb.set_trace()
    # mger.create("tool_local", debug=True)
    mger.create("tool_git", debug=True)


    # mger.remove("tool_local", debug=True)
    # mger.remove("tool_git", debug=True)


    # local based tests
    # mger.create("tool_local", debug=True)
    # mger.remove("tool_local", debug=True)

    # git based tests
    # mger.create("tool_git", debug=True)
    # mger.remove("tool_git", debug=True)
    import pdb; pdb.set_trace()
