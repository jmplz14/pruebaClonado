# -*- coding: utf-8 -*-
#
# This file is part of DNOTA.LIMS
#
# Copyright (c) 2021, DNOTA Medio Ambiente S.L.

from BTrees.OOBTree import OOBTree
from dnota.lims import logger
from dnota.lims import PRODUCT_NAME
from dnota.lims.config import PROFILE_ID
from dnota.lims.config import PROFILE_UNINSTALL_ID
from dnota.lims.utils import set_field_value
from zope.annotation.interfaces import IAnnotations

from bika.lims import api
from bika.lims.browser.analysisrequest.add2 import AR_CONFIGURATION_STORAGE

# Tuples of (field_name, value)
SETUP_SETTINGS = [
    ("title", "DNOTA"),
    ("DefaultCountry", "ES"),
    ("Currency", "EUR"),
    ("VAT", "21"),
    ("MemberDiscount", "5"),
    ("DefaultNumberOfARsToAdd", 1),
    ("ShowPartitions", True)
]

LABORATORY_ADDRESS = {
    "address": "C/Miguel Luesma Castán 4",
    "zip": "50018",
    "city": "Zaragoza",
    "district": "Provincia de Zaragoza",
    "state": "Aragon",
    "country": "Spain",
}

LABORATORY_SETTINGS = [
    ("title", "DNOTA"),
    ("Name", "DNOTA"),
    ("PhysicalAddress", LABORATORY_ADDRESS),
    ("PostalAddress", LABORATORY_ADDRESS),
    ("BillingAddress", LABORATORY_ADDRESS),
    ("Phone", ""),
    ("LabURL", "https://www.dnota.com/"),
]

# Tuples of (id, folder_id)
# If folder_id is None, assume folder_id is portal
ACTIONS_TO_HIDE = [
    ("supplyorders", None),
]

# Skin layers that have priority over others, sorted from more to less priority
SORTED_SKIN_LAYERS = [
    "custom",
    "dnota.lims",
    "bika"
]

# List of field names to not display in Sample Add form
SAMPLE_ADD_FIELDS_TO_HIDE = [
    "PrimaryAnalysisRequest",
]

# An array of dicts. Each dict represents an ID formatting configuration
ID_FORMATTING = [
    {
        "portal_type": "AnalysisRequest",
        "form": "{year}{alpha:2a3d}",
        "prefix": "analysisrequest",
        "sequence_type": "generated",
        "split_length": 1,
    }, {
        "portal_type": "AnalysisRequestPartition",
        "form": "{parent_ar_id}P{partition_count:01d}",
        "prefix": "analysisrequestpartition",
        "sequence_type": "",
        "split-length": 1
    }, {
        "portal_type": "AnalysisRequestSecondary",
        "form": "{parent_ar_id}S{secondary_count:01d}",
        "prefix": "analysisrequestsecondary",
        "sequence_type": "",
        "split-length": 1
    }, {
        "portal_type": "AnalysisRequestRetest",
        "form": "{parent_base_id}R{retest_count:01d}",
        "prefix": "analysisrequestretest",
        "sequence_type": "",
        "split-length": 1
    }, {
        "portal_type": "Worksheet",
        "form": "W{yymmdd}{seq:02d}",
        "prefix": "worksheet",
        "sequence_type": "generated",
        "split_length": 2,
    },
]


def setup_handler(context):
    """Generic setup handler
    """
    install_file = "{}.txt".format(PRODUCT_NAME)
    if context.readDataFile(install_file) is None:
        return

    logger.info("{} setup handler [BEGIN]".format(PRODUCT_NAME.upper()))
    portal = context.getSite()

    # Setup laboratory information
    setup_laboratory(portal)

    # Apply ID format to content types
    setup_id_formatting(portal)

    # Setup the sorting of skin layers
    setup_skin_layers(portal)

    # Hide actions from both navigation portlet and from control_panel
    hide_actions(portal)

    # Hide unused fields from Add Sample form
    hide_sample_add_fields(portal)

    # Reindex the top level folder in the portal
    reindex_content_structure(portal)

    logger.info("{} setup handler [DONE]".format(PRODUCT_NAME.upper()))


def pre_install(portal_setup):
    """Runs before the first import step of the *default* profile
    This handler is registered as a *pre_handler* in the generic setup profile
    :param portal_setup: SetupTool
    """
    logger.info("{} pre-install handler [BEGIN]".format(PRODUCT_NAME.upper()))
    context = portal_setup._getImportContext(PROFILE_ID)  # noqa
    portal = context.getSite()  # noqa portal var not used
    logger.info("{} pre-install handler [DONE]".format(PRODUCT_NAME.upper()))


def post_install(portal_setup):
    """Runs after the last import step of the *default* profile
    This handler is registered as a *post_handler* in the generic setup profile
    :param portal_setup: SetupTool
    """
    logger.info("{} install handler [BEGIN]".format(PRODUCT_NAME.upper()))
    context = portal_setup._getImportContext(PROFILE_ID)  # noqa
    portal = context.getSite()  # noqa portal var not used
    logger.info("{} install handler [DONE]".format(PRODUCT_NAME.upper()))


def post_uninstall(portal_setup):
    """Runs after the last import step of the *uninstall* profile
    This handler is registered as a *post_handler* in the generic setup profile
    :param portal_setup: SetupTool
    """
    logger.info("{} uninstall handler [BEGIN]".format(PRODUCT_NAME.upper()))
    context = portal_setup._getImportContext(PROFILE_UNINSTALL_ID)  # noqa
    portal = context.getSite()  # noqa portal var not used
    logger.info("{} uninstall handler [DONE]".format(PRODUCT_NAME.upper()))


def setup_laboratory(portal):
    """Setup Laboratory
    """
    logger.info("Setup Laboratory ...")
    setup = api.get_setup()

    # Apply general settings
    for field_name, value in SETUP_SETTINGS:
        set_field_value(setup, field_name, value)

    # Laboratory information
    lab = setup.laboratory
    for field_name, value in LABORATORY_SETTINGS:
        set_field_value(lab, field_name, value)

    lab.reindexObject()
    logger.info("Setup Laboratory [DONE]")


def setup_id_formatting(portal, format_definition=None):
    """Setup default ID formatting
    """
    if not format_definition:
        logger.info("Setting up ID formatting ...")
        for formatting in ID_FORMATTING:
            setup_id_formatting(portal, format_definition=formatting)
        logger.info("Setting up ID formatting [DONE]")
        return

    bs = portal.bika_setup
    p_type = format_definition.get("portal_type", None)
    if not p_type:
        return

    form = format_definition.get("form", "")
    if not form:
        logger.info("Param 'form' for portal type {} not set [SKIP")
        return

    logger.info("Applying format '{}' for {}".format(form, p_type))
    ids = list()
    for record in bs.getIDFormatting():
        if record.get('portal_type', '') == p_type:
            continue
        ids.append(record)
    ids.append(format_definition)
    bs.setIDFormatting(ids)


def setup_skin_layers(portal):
    """Setup the sorting of skin layers
    """
    logger.info("Setup Skin layers ...")
    skins_tool = api.get_tool("portal_skins")
    selections = skins_tool._getSelections()

    # For each skin, resort the skins layers in accordande
    for skin_name in selections.keys():
        layers = selections[skin_name].split(",")
        filtered = filter(lambda layer: layer not in SORTED_SKIN_LAYERS, layers)
        new_layers = SORTED_SKIN_LAYERS + filtered
        selections[skin_name] = ",".join(new_layers)

    logger.info("Setup Skin layers [DONE]")


def hide_actions(portal):
    """Excludes actions from both navigation portlet and from control_panel
    """
    logger.info("Hiding actions ...")
    for action_id, folder_id in ACTIONS_TO_HIDE:
        if folder_id and folder_id not in portal:
            logger.info("{} not found in portal [SKIP]".format(folder_id))
            continue
        folder = folder_id and portal[folder_id] or portal
        hide_action(folder, action_id)


def hide_action(folder, action_id):
    logger.info("Hiding {} from {} ...".format(action_id, folder.id))
    if action_id not in folder:
        logger.info("{} not found in {} [SKIP]".format(action_id, folder.id))
        return

    item = folder[action_id]
    logger.info("Hide {} ({}) from nav bar".format(action_id, item.Title()))
    if api.is_dexterity_content(item):
        item.exclude_from_nav = True
    else:
        item.setExcludeFromNav(True)
    item.reindexObject()

    def get_action_index(action_id):
        for n, action in enumerate(cp.listActions()):
            if action.getId() == action_id:
                return n
        return -1

    logger.info("Hide {} from control_panel".format(action_id, item.Title()))
    cp = api.get_tool("portal_controlpanel")
    action_index = get_action_index(action_id)
    if action_index == -1:
        logger.info("{}  not found in control_panel [SKIP]".format(cp.id))
        return

    actions = cp._cloneActions()  # noqa
    del actions[action_index]
    cp._actions = tuple(actions)
    cp._p_changed = 1


def reindex_content_structure(portal):
    """Reindex contents generated by Generic Setup
    """
    logger.info("Reindex content structure ...")
    for obj in portal.objectValues():
        if not api.is_object(obj):
            continue
        logger.info("Reindexing {}".format(repr(obj)))
        if hasattr(obj, "setExpirationDate"):
            obj.setExpirationDate(None)
        obj.reindexObject()

    logger.info("Reindex content structure [DONE]")


def get_manage_add_storage(portal):
    """Returns the annotations storage containing the field settings for the
    Sample Add form
    """
    bika_setup = portal.bika_setup
    annotation = IAnnotations(bika_setup)
    storage = annotation.get(AR_CONFIGURATION_STORAGE)
    if storage is None:
        annotation[AR_CONFIGURATION_STORAGE] = OOBTree()
    return annotation[AR_CONFIGURATION_STORAGE]


def update_manage_add_storage(portal, storage):
    """Updates the annotations storage containing the fields settings for the
    Sample add form with the settings provided
    """
    bika_setup = portal.bika_setup
    annotation = IAnnotations(bika_setup)
    annotation[AR_CONFIGURATION_STORAGE] = storage


def hide_sample_add_fields(portal):
    """Hides unused fields from AR Add Form
    """
    logger.info("Hiding default fields from AR Add ...")
    storage = get_manage_add_storage(portal)
    visibility = storage.get('visibility', {}).copy()
    ordered = storage.get('order', [])
    fields = list(set(visibility.keys() + SAMPLE_ADD_FIELDS_TO_HIDE + ordered))
    for field_name in fields:
        visibility[field_name] = field_name not in SAMPLE_ADD_FIELDS_TO_HIDE
    storage.update({"visibility": visibility})
    update_manage_add_storage(portal, storage)
    logger.info("Hiding default fields from AR Add [DONE]")
