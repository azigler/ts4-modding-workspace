# CREDIT: thepancake1 and MizoreYukii 
# LINK: https://discord.com/channels/605863047654801428/628038777134383119/804415802798768181

import sims4.commands
import sims4.reload
import sims4.reload_service
import sims4.tuning.tunable
import sims4.callback_utils
import sims4.log
import sims4.core_services
import sims4.tuning.serialization
import sims4.log
import sys
import linecache
import os
from settings import scripting_mods_folder

@sims4.commands.Command('r.script', command_type=sims4.commands.CommandType.Live)
def hot_reload(*args, _connection=None):
    output = sims4.commands.Output(_connection)
    if not args:
        sims4.reload.trigger_reload(output)
    else:
        mod = args[0]
        module = sys.modules.get(args[1])
        if module is None:
            output('No module found...'.format(module))
        elif not hasattr(module, '__file__'):
            output('Could not reload built-in module: {}'.format(module))
        else:
            reload_file(module.__file__, mod, output)

def reload_file(filename, mod, output):
    module = sims4.reload.get_module_for_filename(filename)
    reloaded_module = None
    if module is None:
        output('No module found: {}'.format(filename))
        return
    reloaded_module = _reload(module, filename, mod, output)
    try:
        sims4.tuning.serialization.process_tuning(module)
    except:
        output('Exception encountered while reloading module: {}'.format(filename))
    linecache.checkcache(filename)
    if reloaded_module is not None:
        return reloaded_module

def _reload(module, filename, mod, output):
    modns = module.__dict__
    rest, file = os.path.split(module.__file__)
    file = file[:-1]
    code = None
    try:
        code = compile(open(os.path.join(scripting_mods_folder, mod, file)).read(), mod, 'exec')
        output('Reloaded {}'.format(filename))
    except:
        output('Exception encountered while reloading from {}'.format(scripting_mods_folder, mod, file))
    if code is not None:
        tmpns = modns.copy()
        modns.clear()
        modns['__name__'] = tmpns['__name__']
        modns['__file__'] = tmpns['__file__']
        exec(code, modns)
        sims4.reload.update_module_dict(tmpns, modns)
        return module
