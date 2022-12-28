# pylint: disable=no-member
# type: ignore
"""Security Rules"""

from copy import copy
import json

from prismasase import logger
from prismasase import return_auth, config
from prismasase.configs import Auth
from prismasase.restapi import prisma_request
from prismasase.utilities import default_params
from prismasase.exceptions import SASEMissingParam

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
    FOLDERS = ['Shared', 'Mobile Users', 'Remote Networks', 'Service Connections',
               'Mobile Users Container', 'Mobile Users Explicit Proxy']
    POSITION = ['pre', 'post']
    URL = f"{config.REST_API['security-rules']}"
    URL_TYPE = 'security-rules'
    SECURITY_RULES_ATTRIBUTES = {
        'security_rules_id': str,
        'action': str,  # rquired
        'application': list,  # required
        'category': list,  # required
        'description': str,
        'destination': list,  # required
        'destination_hip': list,
        'disabled': bool,
        'zone_from': list,  # required
        'log_setting': str,
        'negate_destination': bool,
        'negate_source': bool,
        'profile_setting': dict,
        'service': list,  # required
        'source': list,  # required
        'source_hip': list,
        'source_user': list,  # required
        'tag': list,
        'zone_to': list  # required
    }
    ACTIONS = ['drop', 'allow']

    def __init__(self, **kwargs):
        self.auth: Auth = return_auth(**kwargs)
        try:
            kwargs.pop('auth')
        except KeyError:
            prisma_logger.info(
                "Could not find \"auth\" in passed parameters; creating auth from config")
        for i, k in self.SECURITY_RULES_ATTRIBUTES.items():
            setattr(self, i, kwargs.pop(i) if kwargs.get(i)
                    and isinstance(kwargs.get(i), k) else k())
        self.params = default_params(**kwargs)
        self.__name = kwargs.pop('name', '')
        self.__folder = kwargs.pop('folder', '')
        self.__position = kwargs.pop('position', '')
        self.current_payload = {}
        self.previous_payload = {}
        self.created_rules = []
        self.current_rulebase = {}
        self.deleted_rules = []
        self._kwargs = kwargs

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

    @property
    def folder(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        return self.__folder

    @folder.setter
    def folder(self, value):
        self.__folder = value

    @folder.deleter
    def folder(self):
        del self.__folder

    @property
    def position(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        return self.__position

    @position.setter
    def position(self, value):
        self.__position = value

    @position.deleter
    def position(self):
        del self.__position

    def _reset_values_empty(self):
        for i, k in self.SECURITY_RULES_ATTRIBUTES.items():
            setattr(self, i, k())

    def _reset_values_new(self, **kwargs):
        for i, k in self.SECURITY_RULES_ATTRIBUTES.items():
            setattr(self, i, kwargs.pop(i) if kwargs.get(i)
                    and isinstance(kwargs.get(i), k) else k())

    def security_rules_list(self):
        """_summary_

        Returns:
            _type_: _description_
        """
        return self._security_rules_list(return_response=True)

    def _security_rules_list(self, return_response=False):
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
        params = {**self.params, **{'folder': self.folder, 'position': self.position}}
        while (len(data) < response['total'] or count == 0):
            response = prisma_request(token=self.auth,
                                      method="GET",
                                      params=params,
                                      url_type=self.URL_TYPE,
                                      verify=self.auth.verify)
            data = data + response['data']
            params = {**params, **{'offset': params['offset'] + params['limit']}}
            count += 1
        response['data'] = data
        self._security_rules_reformat_to_json(security_rule_list=data)
        prisma_logger.info(
            "Retrieved Current Security Rule List for folder=%s position=%s",
            self.folder,
            self.position)
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

    def security_rules_create(self, reset_values: bool = False, **kwargs) -> dict:
        """_summary_

        Args:
            reset_values (bool, optional): _description_. Defaults to False.

        Returns:
            _type_: _description_
        """
        # reset values with new kwarg arguments being passed
        if kwargs.get('name'):
            self.__name = kwargs.pop('name')
        if kwargs.get('folder'):
            self.__folder = kwargs.pop('folder')
        if kwargs.get('position'):
            self.__position = kwargs.pop('position')
        if reset_values:
            self._reset_values_new(**kwargs)
        self.security_rules_create_payload()
        params = {'folder': self.folder, 'position': self.position}
        response = prisma_request(token=self.auth,
                                  method="POST",
                                  url_type=self.URL_TYPE,
                                  params=params,
                                  data=json.dumps(self.current_payload),
                                  verify=self.auth.verify)
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
        if not folder and not self.folder:
            raise SASEMissingParam("message=\"requires folder\"")
        if not security_rules_id:
            security_rules_id = self.security_rules_id
        if not folder:
            folder = self.folder
        params = {'folder': folder}
        response = prisma_request(token=self.auth,
                                  method="GET",
                                  params=params,
                                  url_type=self.URL_TYPE,
                                  verify=self.auth.verify,
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
        if not folder and not self.folder:
            raise SASEMissingParam("message=\"requires folder\"")
        if not security_rules_id:
            security_rules_id = self.security_rules_id
        if not folder:
            folder = self.folder
        params = {'folder': folder}
        response = prisma_request(token=self.auth,
                                  method='DELETE',
                                  url_type=self.URL_TYPE,
                                  params=params,
                                  delete_object=f"/{security_rules_id}",
                                  verify=self.auth.verify)
        prisma_logger.info("Deleted Rule: %s", (response))
        self.deleted_rules.append(response)
        self._update_current_rulebase(to_do='delete', rule=[response])
        return response

    def security_rules_edit(self):
        pass

    def _update_current_rulebase(self, to_do: str, rule: list) -> None:
        if to_do == 'delete':
            if self.current_rulebase.get(self.folder):
                if self.current_rulebase[self.folder].get(rule[0]['id']):
                    self.current_rulebase[self.folder].pop(rule[0]['id'])
            else:
                self._security_rules_list()
        if to_do == 'create':
            if self.current_rulebase.get(self.folder):
                self._security_rules_reformat_to_json(security_rule_list=rule)
            else:
                self._security_rules_list()
        # TODO: Build Edit to current rulebase
