# pylint: disable=no-member
# type: ignore
"""Security Rules"""

from copy import copy
import json

from prismasase import logger
from prismasase.restapi import prisma_request
from prismasase.exceptions import SASEMissingParam, SASEBadParam

logger.addLogger(__name__)
prisma_logger = logger.getLogger(__name__)


class SecurityRules:
    """_summary_

    Args:
        object (_type_): _description_

    Raises:
        SASEMissingParam: _description_

    Returns:
        _type_: _description_
    """
    # placeholder for parent class namespace
    _parent_class = None

    url_type = 'security-rules'
    security_rules_id = None
    """Security Rule ID"""

    __action: str = 'allow'  # required
    application: list = ['any']  # required
    category: list = ['any']  # required
    description: str = ''
    destination: list = ['any']  # required
    destination_hip: list = []
    disabled: bool = False
    zone_from: list = ['any']  # required
    log_setting: str = ''
    negate_destination: bool = False
    negate_source: bool = False
    profile_setting: dict = {}
    service: list = ['any']  # required
    source: list = ['any']  # required
    source_hip: list = []
    source_user: list = ['any']  # required
    tag: list = []
    zone_to: list = []  # required

    ACTIONS = ['drop', 'allow']

    __name = ''
    current_payload = {}
    previous_payload = {}
    created_rules = []
    current_rulebase = {}
    deleted_rules = []

    @property
    def action(self):
        """_summary_

        Raises:
            SASEMissingParam: _description_

        Returns:
            _type_: _description_
        """
        if self.__action not in self.ACTIONS:
            raise SASEBadParam(str(self.__action))
        return self.__action

    @action.setter
    def action(self, value):
        if value not in self.ACTIONS:
            raise SASEBadParam(str(value))
        self.__action = value

    @property
    def name(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        return self.__name

    @name.setter
    def name(self, value):
        self.__name = value

    @name.deleter
    def name(self):
        del self.__name

    def _reset_values_default(self):
        defaults = {
            'name': '',
            'action': 'allow',
            'description': '',
            'application': ['any'],
            'category': ['any'],
            'destination': ['any'],
            'destination_hip': ['any'],
            'disabled': False,
            'zone_from': ['any'],
            'log_setting': 'Cortex Data Lake',
            'negate_destination': False,
            'negate_source': False,
            'service': ['any'],
            'source': ['any'],
            'source_hip': ['any'],
            'source_user': ['any'],
            'zone_to': ['any']
        }
        for i, k in defaults.items():
            setattr(self, i, k)

    def _reset_values_new(self, **kwargs):
        for i, k in kwargs.items():
            setattr(self, i, k)

    def security_rules_list(self, **kwargs):
        """_summary_

        Returns:
            _type_: _description_
        """
        return self._security_rules_list(return_response=True, **kwargs)

    def _security_rules_list(self, return_response=False, **kwargs):
        """_summary

        Returns:
            _type_: _description_
        """
        data = []
        count = 0
        response = {
            'data': [],
            'offset': 0,
            'total': 0,
            'limit': 0
        }
        folder = kwargs.get('folder') if kwargs.get('folder') and kwargs.get(
            'folder') in self._parent_class.FOLDERS else self._parent_class.folder
        self._parent_class.folder = folder
        position = kwargs.get('position') if kwargs.get('position') and kwargs.get(
            'position') in self._parent_class.POSITION else self._parent_class.position
        self._parent_class.position = position
        params = {**self._parent_class.params, **{'folder': folder, 'position': position}}
        while (len(data) < response['total'] or count == 0):
            response = prisma_request(token=self._parent_class.auth,
                                      method="GET",
                                      params=params,
                                      url_type=self.url_type,
                                      verify=self._parent_class.auth.verify)
            data = data + response['data']
            params = {**params, **{'offset': params['offset'] + params['limit']}}
            count += 1
        response['data'] = data
        self._security_rules_reformat_to_json(security_rule_list=data)
        prisma_logger.info(
            "Retrieved Current Security Rule List for folder=%s position=%s",
            folder,
            position)
        prisma_logger.debug("Security Rules List = %s", (json.dumps(response)))
        if return_response:
            return response

    def security_rules_create_payload(self) -> None:
        """_summary_

        Raises:
            SASEMissingParam: _description_
        """
        # required params
        if not self.name:
            raise SASEMissingParam("message=\"missing name parameter\"")
        if not self.action:
            raise SASEMissingParam(f"message=\"missing {str(self.action)}\"")

        data = {
            "name": self.name,
            "action": self.action,
            "application": self.application if self.application else ['any'],
            "category": self.category if self.category else ['any'],
            "destination": self.destination if self.destination else ['any'],
            "destination_hip": self.destination_hip if self.destination_hip else ['any'],
            "disabled": self.disabled,
            "from": self.zone_from if self.zone_from else ['any'],
            "log_setting": self.log_setting if self.log_setting else 'Cortex Data Lake',
            "negate_destination": self.negate_destination,
            "negate_source": self.negate_source,
            "service": self.service if self.service else ['application-default'],
            "source": self.source if self.source else ['any'],
            "source_hip": self.source_hip if self.source_hip else ['any'],
            "source_user": self.source_user if self.source_user else ['any'],
            "to": self.zone_to if self.zone_to else ['any']
        }
        if self.description:
            data["description"] = self.description
        if self.profile_setting:
            data["profile_setting"] = self.profile_setting
        if self.tag:
            data["tag"] = self.tag
        self.previous_payload = copy(self.current_payload)
        self.current_payload = data

    def __repr__(self) -> str:
        attrs = str([x for x in self.__dict__])
        return attrs

    def security_rules_create(self, **kwargs) -> dict:
        """_summary_

        Args:
            reset_values (bool, optional): _description_. Defaults to False.

        Returns:
            _type_: _description_
        """
        # reset values with new kwarg arguments being passed
        if kwargs.get('name'):
            self.__name = kwargs.pop('name')
        if kwargs.get('action'):
            self.__action = kwargs.pop('action')
        if kwargs.get('folder'):
            self._parent_class.folder = kwargs.pop('folder')
        if kwargs.get('position'):
            self._parent_class.position = kwargs.pop('position')
        self._reset_values_new(**kwargs)
        self.security_rules_create_payload()
        params = {'folder': self._parent_class.folder, 'position': self._parent_class.position}
        response = prisma_request(token=self._parent_class.auth,
                                  method="POST",
                                  url_type=self.url_type,
                                  params=params,
                                  data=json.dumps(self.current_payload),
                                  verify=self._parent_class.auth.verify)
        prisma_logger.info("Created Rule: %s", (response))
        self.created_rules.append(response)
        self._update_current_rulebase(to_do='create', rule=[response])
        return response

    def security_rules_get(self, security_rules_id: str = None, folder: str = None) -> dict:
        """Get Security Rule by ID

        Args:
            security_rules_id (str, optional): _description_. Defaults to None.
            folder (str, optional): _description_. Defaults to None.

        Raises:
            SASEMissingParam: _description_
            SASEMissingParam: _description_

        Returns:
            dict: _description_
        """
        if not security_rules_id and not self.security_rules_id:
            raise SASEMissingParam("message=\"requires security rule ID param\"")
        if not folder and not self._parent_class.folder:
            raise SASEMissingParam("message=\"requires folder\"")
        if not security_rules_id:
            security_rules_id = self.security_rules_id
        if not folder:
            folder = self._parent_class.folder
        params = {'folder': folder}
        response = prisma_request(token=self._parent_class.auth,
                                  method="GET",
                                  params=params,
                                  url_type=self.url_type,
                                  verify=self._parent_class.auth.verify,
                                  get_object=f"/{security_rules_id}")
        prisma_logger.info("Retrieved Security Rule ID: %s", self.security_rules_id)
        return response

    def _security_rules_reformat_to_json(self, security_rule_list: list) -> None:
        """Creates a formated hierarchy structure of all rulesets and updates them as they change.

        Args:
            security_rule_list (list): _description_
        """
        for rule in security_rule_list:
            if rule['folder'] not in list(self.current_rulebase):
                self.current_rulebase.update({rule['folder']: {}})
            if rule['position'] not in list(self.current_rulebase[rule['folder']]):
                self.current_rulebase[rule['folder']].update({rule['position']: {}})
            self.current_rulebase[rule['folder']][rule['position']].update({rule['id']: rule})

    def security_rules_delete(self, security_rules_id: str = None, folder: str = None):
        """_summary_

        Args:
            security_rules_id (str, optional): _description_. Defaults to None.
            folder (str, optional): _description_. Defaults to None.

        Raises:
            SASEMissingParam: _description_
            SASEMissingParam: _description_

        Returns:
            _type_: _description_
        """
        if not security_rules_id and not self.security_rules_id:
            raise SASEMissingParam("message=\"requires security rule ID param\"")
        if not folder and not self._parent_class.folder:
            raise SASEMissingParam("message=\"requires folder\"")
        if not security_rules_id:
            security_rules_id = self.security_rules_id
        else:
            self.security_rules_id = security_rules_id
        if not folder:
            folder = self._parent_class.folder
        params = {'folder': folder}
        response = prisma_request(token=self._parent_class.auth,
                                  method='DELETE',
                                  url_type=self.url_type,
                                  params=params,
                                  delete_object=f"/{security_rules_id}",
                                  verify=self._parent_class.auth.verify)
        prisma_logger.info("Deleted Rule: %s", (response))
        self.deleted_rules.append(response)
        self._update_current_rulebase(to_do='delete', rule=[response])
        return response

    def security_rules_edit(self):
        pass

    def _update_current_rulebase(self, to_do: str, rule: list) -> None:
        if to_do == 'delete':
            if not rule[0].get('position'):
                # set default position as is not returned in delete when deleting in non 'Shared'
                rule[0]['position'] = 'pre'
            if self.current_rulebase.get(rule[0]['folder']):
                if self.current_rulebase[rule[0]['folder']][rule[0]['position']].get(rule[0]['id']):
                    deleted_rule = self.current_rulebase[rule[0][
                        'folder']][rule[0]['position']].pop(rule[0]['id'])
                    prisma_logger.debug("Removed from current_rulebase: %s", (deleted_rule))
            else:
                self._security_rules_list()
        if to_do == 'create':
            self._security_rules_list()
        # TODO: Build Edit to current rulebase