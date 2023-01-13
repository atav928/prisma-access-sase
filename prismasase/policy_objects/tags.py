# type: ignore
"""Tags"""

import json

from prismasase import return_auth, logger
from prismasase.configs import Auth
from prismasase.exceptions import (SASEError, SASEMissingParam,
                                   SASEObjectExists, SASEIncorrectParam)
from prismasase.restapi import (prisma_request, default_list_all)
from prismasase.statics import FOLDER, TAG_COLORS
from prismasase.utilities import (default_params, reformat_exception, verify_valid_folder)

logger.addLogger(__name__)
prisma_logger = logger.getLogger(__name__)


class Tags:
    """Tag Subclass Moudule

    Raises:
        SASEIncorrectParam: _description_
        SASEMissingParam: _description_

    Returns:
        _type_: _description_
    """
    # placeholder for parent class namespace
    _parent_class = None

    url_type: str = "tags"
    __name: str = ''
    __color: str = 'Empty'
    comment: str = ''
    tag_id: str = ''
    current_tag_payload: dict = {}
    previous_tag_payload: dict = {}
    current_tags: dict = {}

    TAG_COLORS = TAG_COLORS

    @property
    def name(self):
        """Tag Name"""
        return self.__name

    @name.setter
    def name(self, value):
        self.__name = value

    @property
    def color(self):
        """Tag Color"""
        try:
            Tags.check_valid_color(self.__color)
            return self.__color
        except SASEIncorrectParam as err:
            error = reformat_exception(error=err)
            prisma_logger.error("Invalid color set: %s, valid colors are: %s, error=%s",
                                self.__color, ','.join(self.TAG_COLORS), error)

    @color.setter
    def color(self, value):
        try:
            # reformat color value since format is Capital first letter
            Tags.check_valid_color(value.title())
            self.__color = value.title()
        except SASEIncorrectParam as err:
            error = reformat_exception(error=err)
            prisma_logger.error("Invalid color set: %s, valid colors are: %s, error=%s",
                                value, ','.join(self.TAG_COLORS), error)

    @staticmethod
    def check_valid_color(color) -> None:
        """Check if Color being set is valid

        Args:
            color (_type_): _description_

        Raises:
            SASEIncorrectParam: _description_
        """
        if color not in TAG_COLORS:
            raise SASEIncorrectParam(f"message=\"invalid color\"|{color=}")

    def list_all(self, return_value: bool = False, **kwargs):  # pylint: disable=inconsistent-return-statements
        """Get a list of all current tags in folder

        Args:
            return_value (_type_, optional): _description_. Defaults to Fale.

        Returns:
            dict: _description_
        """
        response = self._tags(**kwargs)
        if return_value:
            return response

    def _tags(self, **kwargs) -> dict:
        if kwargs.get('folder'):
            try:
                verify_valid_folder(folder=kwargs['folder'])
                self._parent_class.folder = kwargs['folder']
            except SASEIncorrectParam as err:
                error = reformat_exception(error=err)
                prisma_logger.error("Invalid Folder error=%s", error)
        if not self._parent_class.folder:
            prisma_logger.error("Folder is not set and a required param")
            raise SASEMissingParam("Folder not set")
        # response = tags_list(folder=self._parent_class.folder, auth=self._parent_class.auth)
        response = default_list_all(folder=self._parent_class.folder,
                                    url_type=self.url_type,
                                    auth=self._parent_class.auth)
        self._tags_reformat_to_json(tag_list=response['data'])
        prisma_logger.info("Gathered list of all tags in folder=%s", self._parent_class.folder)
        return response

    def _tags_reformat_to_json(self, tag_list) -> None:
        for tag in tag_list:
            if tag['folder'] == 'predefined':
                # predefined has no ID or UUID to make it unique so pass
                continue
            if tag['folder'] not in list(self.current_tags):
                self.current_tags.update({tag['folder']: {}})
            self.current_tags[tag['folder']].update({tag['id']: tag})


def tags_list(folder: str, **kwargs) -> dict:
    """List out all tags in the specified folder

    Args:
        folder (str): _description_

    Returns:
        dict: _description_
    """
    try:
        verify_valid_folder(folder=folder)
    except SASEIncorrectParam as err:
        error = reformat_exception(error=err)
        prisma_logger.error("Incorrect value for Folder error=%s", error)
    response = default_list_all(folder=folder, url_type='tags', **kwargs)
    return response


def tags_create(folder: str, tag_name: str, **kwargs) -> dict:
    """Create Tag

    Args:
        folder (str): _description_

    Returns:
        dict: _description_
    """
    auth: Auth = return_auth(**kwargs)
    response = {}
    params = default_params(**kwargs)
    params = {**FOLDER[folder], **params}
    # Verify that tag doesn't already exist
    tags_get_tag = tags_get(folder=folder, tag_name=tag_name)
    if tags_get_tag:
        raise SASEObjectExists(f"Object already exists tag={tag_name}")
    data = tags_create_data(tag_name=tag_name, **kwargs)
    prisma_logger.debug("Tag data created %s", data)
    response = prisma_request(token=auth,
                              method="POST",
                              url_type='tags',
                              params=params,
                              data=json.dumps(data),
                              verify=auth.verify)
    return response


def tags_get(folder: str, tag_name: str, **kwargs) -> dict:
    """Retrieve a Tag if it exists empty dict if none is found

    Args:
        folder (str): _description_
        tag_name (str): _description_

    Returns:
        dict: _description_
    """
    # Will now loop through get all tags offseting by 500 each time
    auth: Auth = return_auth(**kwargs)
    response = {}
    tag_get_list = tags_list(folder=folder, limit=500, auth=auth)
    tag_get_list = tag_get_list['data']
    for tag in tag_get_list:
        if tag_name == tag['name']:
            response = tag
            prisma_logger.info("Fopund Tag: %s", {response})
            # print(f"INFO: Found Tag: {response}")
            break
    return response


def tags_create_data(tag_name: str, **kwargs) -> dict:
    """Creates tag Data Structure

    Args:
        tag_name (str): Name for Tag
        tag_color (str, Optional): Color for tag, must be part of predefined list
        tag_comments (str, Optional): Comment for Tag

    Returns:
        dict: data structure for rest call
    """
    data = {'name': tag_name}
    if kwargs.get('tag_comments'):
        data.update({'comments': kwargs['tag_comments']})
    if kwargs.get('tag_color') and kwargs.get('tag_color') in TAG_COLORS:
        data.update({'color': kwargs['tag_color']})
    return data


def tags_exist(tag_list: list, folder: str, **kwargs) -> bool:
    """Verifies if tag exists in configs

    Args:
        tag_list (list): _description_
        folder (str): _description_

    Raises:
        SASEError: _description_

    Returns:
        bool: _description_
    """
    if not isinstance(tag_list, list):
        prisma_logger.error("SASEError: requires a list of tagnames tag_list=%s", (tag_list))
        raise SASEError(f"message=\"requires a list of tagnames\"|{tag_list=}")
    for tag in tag_list:
        if not tags_get(tag_name=tag, folder=folder, **kwargs):
            prisma_logger.debug("Tag doesnot exist: %s", (tag))
            # print(f"DEBUG: {tag=} doesnot exist")
            return False
    return True


def tags_get_by_id(tag_id: str, folder: str, **kwargs) -> dict:
    """Get Tag by ID

    Args:
        tag_id (str): Requires TAG ID
        folder (str): Currently requires folder to be defined

    Returns:
        dict: _description_
    """
    auth: Auth = return_auth(**kwargs)
    params = FOLDER[folder]
    response = prisma_request(token=auth,
                              method="POST",
                              url_type='tags',
                              params=params,
                              get_object=f'/{tag_id}',
                              verify=auth.verify)
    return response
