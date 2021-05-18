# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from openapi_server.models.base_model_ import Model
from openapi_server.models.any_type import AnyType
from openapi_server import util

from openapi_server.models.any_type import AnyType  # noqa: E501

class OperationOverlay(Model):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.
    """

    def __init__(self, id=None, parameters=None):  # noqa: E501
        """OperationOverlay - a model defined in OpenAPI

        :param id: The id of this OperationOverlay.  # noqa: E501
        :type id: str
        :param parameters: The parameters of this OperationOverlay.  # noqa: E501
        :type parameters: AnyType
        """
        self.openapi_types = {
            'id': str,
            'parameters': AnyType
        }

        self.attribute_map = {
            'id': 'id',
            'parameters': 'parameters'
        }

        self._id = id
        self._parameters = parameters

    @classmethod
    def from_dict(cls, dikt) -> 'OperationOverlay':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The OperationOverlay of this OperationOverlay.  # noqa: E501
        :rtype: OperationOverlay
        """
        return util.deserialize_model(dikt, cls)

    @property
    def id(self):
        """Gets the id of this OperationOverlay.


        :return: The id of this OperationOverlay.
        :rtype: str
        """
        return self._id

    @id.setter
    def id(self, id):
        """Sets the id of this OperationOverlay.


        :param id: The id of this OperationOverlay.
        :type id: str
        """
        allowed_values = ["overlay"]  # noqa: E501
        if id not in allowed_values:
            raise ValueError(
                "Invalid value for `id` ({0}), must be one of {1}"
                .format(id, allowed_values)
            )

        self._id = id

    @property
    def parameters(self):
        """Gets the parameters of this OperationOverlay.


        :return: The parameters of this OperationOverlay.
        :rtype: AnyType
        """
        return self._parameters

    @parameters.setter
    def parameters(self, parameters):
        """Sets the parameters of this OperationOverlay.


        :param parameters: The parameters of this OperationOverlay.
        :type parameters: AnyType
        """

        self._parameters = parameters
