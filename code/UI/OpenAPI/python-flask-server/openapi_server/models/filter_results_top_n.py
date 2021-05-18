# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from openapi_server.models.base_model_ import Model
from openapi_server import util


class FilterResultsTopN(Model):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.
    """

    def __init__(self, max_results=None):  # noqa: E501
        """FilterResultsTopN - a model defined in OpenAPI

        :param max_results: The max_results of this FilterResultsTopN.  # noqa: E501
        :type max_results: int
        """
        self.openapi_types = {
            'max_results': int
        }

        self.attribute_map = {
            'max_results': 'max_results'
        }

        self._max_results = max_results

    @classmethod
    def from_dict(cls, dikt) -> 'FilterResultsTopN':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The FilterResultsTopN of this FilterResultsTopN.  # noqa: E501
        :rtype: FilterResultsTopN
        """
        return util.deserialize_model(dikt, cls)

    @property
    def max_results(self):
        """Gets the max_results of this FilterResultsTopN.

        The maximum number of results to return.  # noqa: E501

        :return: The max_results of this FilterResultsTopN.
        :rtype: int
        """
        return self._max_results

    @max_results.setter
    def max_results(self, max_results):
        """Sets the max_results of this FilterResultsTopN.

        The maximum number of results to return.  # noqa: E501

        :param max_results: The max_results of this FilterResultsTopN.
        :type max_results: int
        """
        if max_results is None:
            raise ValueError("Invalid value for `max_results`, must not be `None`")  # noqa: E501

        self._max_results = max_results
