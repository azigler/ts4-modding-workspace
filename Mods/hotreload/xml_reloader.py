# CREDIT: thepancake1 and MizoreYukii 
# LINK: https://discord.com/channels/605863047654801428/628038777134383119/804415802798768181

import glob
import io
import os
import xml
import services
import sims4
import sims4.tuning
import services
from server_commands.tuning_commands import get_managers
from sims4.resources import ResourceLoader
from sims4.tuning.instance_manager import TUNING_LOADED_CALLBACK, VERIFY_TUNING_CALLBACK
from sims4.tuning.module_tuning import _ParseHandler, _EarlyExit
from sims4.tuning.serialization import ETreeTuningLoader, ETreeClassCreator, _find_tunables_gen, LOAD_MODULE_FOR_EXPORTING, _scan_module_rec
from sims4.tuning.tunable_base import LoadingTags
from sims4.utils import strformatter
from settings import hotreload_folder

logger = sims4.log.Logger('XML Reloader', default_owner='thepancake1')
reload_keys = {"interaction" : [sims4.resources.Key(0xE882D22F, 0x0000000000006A25, 0x00000000)]}

@sims4.commands.Command('r.xml')
def tuning_reload(_connection=None):
    sims4.callback_utils.invoke_callbacks(sims4.callback_utils.CallbackEvent.TUNING_CODE_RELOAD)
    done = set()
    dependents = set()

    def update(changed):
        done.add(changed)
        logger.debug("{}".format(manager))
        new_dependents, file_name = reload_by_key(manager, changed)
        if new_dependents is False:
            sims4.commands.output('Failed to reload XML: {}'.format(changed), _connection)
        else:
            sims4.commands.output('Reloaded: {}'.format(os.path.basename(file_name)), _connection)
            dependents.update(new_dependents)
    
    for manager in get_managers().values():
        manager_name = manager.TYPE.name.lower()
        if manager_name in reload_keys:
            for changed in reload_keys[manager_name]:
                logger.debug("{}".format(changed))
                update(changed)

    services.definition_manager().refresh_build_buy_tag_cache()
    sims4.resources.cache_localwork()
    sims4.commands.output('Reloading complete!', _connection)
    return True

def get_module_name_from_tuning(key):
    loader = InjectorResourceLoader(key)
    tuning_file = loader.load()[0]
    parse_handler = _ParseHandler()
    try:
        xml.sax.parse(tuning_file, parse_handler)
    except _EarlyExit:
        return parse_handler.module_name

def load_module_tuning(module, tuning_filename_or_key):
    schema_dict = {}
    has_tunables = _scan_module_rec(schema_dict, module, LoadingTags.Module, module.__name__, for_export=False)
    if not has_tunables:
        return True
    if not LOAD_MODULE_FOR_EXPORTING:
        tuning_loader = ETreeTuningLoader(module, tuning_filename_or_key)
        if isinstance(tuning_filename_or_key, str):
            full_name = os.path.basename(tuning_filename_or_key)
            res_name = os.path.splitext(full_name)[0]
            res_key = sims4.resources.get_resource_key(res_name, sims4.resources.Types.TUNING)
        else:
            res_key = tuning_filename_or_key
        loader = InjectorResourceLoader(res_key, sims4.resources.Types.TUNING)
        tuning_file = loader.load()[0]
        tuning_loader.feed(tuning_file)
    for (name, tunable, parent) in _find_tunables_gen(None, schema_dict, module):
        if name in vars(parent):
            if not tunable.deferred:
                tuned_value = getattr(parent, name)
                tunable.invoke_callback(None, name, tuning_filename_or_key, tuned_value)
                value = tunable.default
                reload_context = getattr(parent, '__reload_context__', None)
                if reload_context:
                    with reload_context(parent, parent):
                        setattr(parent, name, value)
                else:
                    setattr(parent, name, value)
        else:
            value = tunable.default
            reload_context = getattr(parent, '__reload_context__', None)
            if reload_context:
                with reload_context(parent, parent):
                    setattr(parent, name, value)
            else:
                setattr(parent, name, value)
    return True

def load_from_xml(resource_key, resource_type, inst, from_reload=False):
    source = strformatter('Instance: {0} ({1}), {2}', resource_key.instance, inst.__name__, resource_type)
    tuning_loader = ETreeTuningLoader(inst, source, loading_tag=LoadingTags.Instance)
    loader = InjectorResourceLoader(resource_key, resource_type)
    tuning_file, file_name = loader.load()
    logger.debug("{} {}".format(tuning_file, file_name))
    logger.debug("XML file is: {}".format(tuning_file))
    if tuning_file is not None:
        return tuning_loader.feed(tuning_file), file_name
    return (None, None)

def create_class(resource_key, resource_type):
    try:
        tuning_loader = ETreeClassCreator()
        loader = InjectorResourceLoader(resource_key, resource_type)
        tuning_file, file_name = loader.load()
        if tuning_file is None:
            logger.debug("No tuning key specified")
            return
        tuning_loader.feed(tuning_file)
        return tuning_loader.module
    except Exception as e:
        logger.error('Exception encountered while creating class instance for resource {} (type: {})...\n {}', resource_key, resource_type, e, owner='manus')
        return

def reload_by_key(self, key):
    reload_dependencies = []
    registered_resource_key = sims4.resources.Key(self.TYPE, key.instance)
    cls = self._tuned_classes.get(registered_resource_key)
    logger.debug("{}".format(self._tuned_classes))
    if cls is None:
        logger.debug("No resource key found")
        cls = create_class(registered_resource_key, self.TYPE)
        logger.debug("CLS {}".format(cls))

        self.register_tuned_class(cls, registered_resource_key)
    try:
        sims4.tuning.serialization.restore_class_instance(cls)
        (tuning_callbacks, verify_callbacks), file_name = load_from_xml(key, self.TYPE, cls, from_reload=True)
        if tuning_callbacks:
            for helper in tuning_callbacks:
                helper.template.invoke_callback(cls, helper.name, helper.source, helper.value)
        if verify_callbacks:
            for helper in verify_callbacks:
                helper.template.invoke_verify_tunable_callback(cls, helper.name, helper.source, helper.value)
        if hasattr(cls, TUNING_LOADED_CALLBACK):
            cls._tuning_loaded_callback()
        if hasattr(cls, VERIFY_TUNING_CALLBACK):
            cls._verify_tuning_callback()
    except Exception as e:
        name = sims4.resources.get_name_from_key(key)
        logger.debug('Failed to reload tuning for {} (key: {})...\n {}', name, key, e)
        return False, False
    return reload_dependencies, file_name

class InjectorResourceLoader(ResourceLoader):
    def cook(self, resource):
        resource = self.try_find_resource()
        if not resource:
            return None, None
        logger.debug("Cooking resource...")
        return io.BytesIO(bytes(open(resource, "rb").read())), resource

    def try_find_resource(self):
        for file in glob.glob(os.path.join(hotreload_folder, "*.xml")):
            t, i = self.resource_key.type, self.resource_key.instance
            truncated_instance = str(hex(i))[2:]
            truncated_type = str(hex(t))[2:]
            split_tgi = file.split("!")
            if split_tgi[2].lower()[:16].endswith(truncated_instance) and split_tgi[0].lower().endswith(truncated_type):
                logger.debug("Found resource: {} {}".format(hex(t), hex(i)))
                return file
            logger.debug("Did not find resource: {} {}".format(hex(t), hex(i)))
