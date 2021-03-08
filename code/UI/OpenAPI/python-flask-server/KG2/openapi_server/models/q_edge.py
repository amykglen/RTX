# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from openapi_server.models.base_model_ import Model
from openapi_server import util


class QEdge(Model):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.
    """

    def __init__(self, predicate=None, relation=None, subject=None, object=None, exclude=None, option_group_id=None):  # noqa: E501
        """QEdge - a model defined in OpenAPI

        :param predicate: The predicate of this QEdge.  # noqa: E501
        :type predicate: List[str]
        :param relation: The relation of this QEdge.  # noqa: E501
        :type relation: str
        :param subject: The subject of this QEdge.  # noqa: E501
        :type subject: str
        :param object: The object of this QEdge.  # noqa: E501
        :type object: str
        :param exclude: The exclude of this QEdge.  # noqa: E501
        :type exclude: bool
        :param option_group_id: The option_group_id of this QEdge.  # noqa: E501
        :type option_group_id: str
        """
        self.openapi_types = {
            'predicate': List[str],
            'relation': str,
            'subject': str,
            'object': str,
            'exclude': bool,
            'option_group_id': str
        }

        self.attribute_map = {
            'predicate': 'predicate',
            'relation': 'relation',
            'subject': 'subject',
            'object': 'object',
            'exclude': 'exclude',
            'option_group_id': 'option_group_id'
        }

        self._predicate = predicate
        self._relation = relation
        self._subject = subject
        self._object = object
        self._exclude = exclude
        self._option_group_id = option_group_id

    @classmethod
    def from_dict(cls, dikt) -> 'QEdge':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The QEdge of this QEdge.  # noqa: E501
        :rtype: QEdge
        """
        return util.deserialize_model(dikt, cls)

    @property
    def predicate(self):
        """Gets the predicate of this QEdge.


        :return: The predicate of this QEdge.
        :rtype: List[str]
        """
        return self._predicate

    @predicate.setter
    def predicate(self, predicate):
        """Sets the predicate of this QEdge.


        :param predicate: The predicate of this QEdge.
        :type predicate: List[str]
        """

        self._predicate = predicate

    @property
    def relation(self):
        """Gets the relation of this QEdge.

        Query constraint against the relationship type term of this edge, as originally specified by, or curated by inference from, the original external source of knowledge. Note that this should often be specified as predicate ontology term CURIE, although this may not be strictly enforced.  # noqa: E501

        :return: The relation of this QEdge.
        :rtype: str
        """
        return self._relation

    @relation.setter
    def relation(self, relation):
        """Sets the relation of this QEdge.

        Query constraint against the relationship type term of this edge, as originally specified by, or curated by inference from, the original external source of knowledge. Note that this should often be specified as predicate ontology term CURIE, although this may not be strictly enforced.  # noqa: E501

        :param relation: The relation of this QEdge.
        :type relation: str
        """

        self._relation = relation

    @property
    def subject(self):
        """Gets the subject of this QEdge.

        Corresponds to the map key identifier of the subject concept node anchoring the query filter pattern for the query relationship edge.  # noqa: E501

        :return: The subject of this QEdge.
        :rtype: str
        """
        return self._subject

    @subject.setter
    def subject(self, subject):
        """Sets the subject of this QEdge.

        Corresponds to the map key identifier of the subject concept node anchoring the query filter pattern for the query relationship edge.  # noqa: E501

        :param subject: The subject of this QEdge.
        :type subject: str
        """
        if subject is None:
            raise ValueError("Invalid value for `subject`, must not be `None`")  # noqa: E501

        self._subject = subject

    @property
    def object(self):
        """Gets the object of this QEdge.

        Corresponds to the map key identifier of the object concept node anchoring the query filter pattern for the query relationship edge.  # noqa: E501

        :return: The object of this QEdge.
        :rtype: str
        """
        return self._object

    @object.setter
    def object(self, object):
        """Sets the object of this QEdge.

        Corresponds to the map key identifier of the object concept node anchoring the query filter pattern for the query relationship edge.  # noqa: E501

        :param object: The object of this QEdge.
        :type object: str
        """
        if object is None:
            raise ValueError("Invalid value for `object`, must not be `None`")  # noqa: E501

        self._object = object

    @property
    def exclude(self):
        """Gets the exclude of this QEdge.

        If set to true, then all subgraphs containing this edge are excluded from the final results. (optional)  # noqa: E501

        :return: The exclude of this QEdge.
        :rtype: bool
        """
        return self._exclude

    @exclude.setter
    def exclude(self, exclude):
        """Sets the exclude of this QEdge.

        If set to true, then all subgraphs containing this edge are excluded from the final results. (optional)  # noqa: E501

        :param exclude: The exclude of this QEdge.
        :type exclude: bool
        """

        self._exclude = exclude

    @property
    def option_group_id(self):
        """Gets the option_group_id of this QEdge.

        Optional string acting as a label on a set of nodes and/or edges indicating that they belong to a group that are to be evaluated as a group.   # noqa: E501

        :return: The option_group_id of this QEdge.
        :rtype: str
        """
        return self._option_group_id

    @option_group_id.setter
    def option_group_id(self, option_group_id):
        """Sets the option_group_id of this QEdge.

        Optional string acting as a label on a set of nodes and/or edges indicating that they belong to a group that are to be evaluated as a group.   # noqa: E501

        :param option_group_id: The option_group_id of this QEdge.
        :type option_group_id: str
        """

        self._option_group_id = option_group_id
