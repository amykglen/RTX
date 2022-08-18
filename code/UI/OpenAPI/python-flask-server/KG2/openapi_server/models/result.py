# coding: utf-8

from __future__ import absolute_import
from datetime import date, datetime  # noqa: F401

from typing import List, Dict  # noqa: F401

from openapi_server.models.base_model_ import Model
from openapi_server.models.edge_binding import EdgeBinding
from openapi_server.models.node_binding import NodeBinding
from openapi_server.models.any_type import AnyType
from openapi_server import util

from openapi_server.models.edge_binding import EdgeBinding  # noqa: E501
from openapi_server.models.node_binding import NodeBinding  # noqa: E501
from openapi_server.models.any_type import AnyType  # noqa: E501

class Result(Model):
    """NOTE: This class is auto generated by OpenAPI Generator (https://openapi-generator.tech).

    Do not edit the class manually.
    """

    def __init__(self, node_bindings=None, edge_bindings=None, id=None, description=None, essence=None, essence_category=None, row_data=None, score=None, score_name=None, score_direction=None, confidence=None, result_group=None, result_group_similarity_score=None, reasoner_id=None):  # noqa: E501
        """Result - a model defined in OpenAPI

        :param node_bindings: The node_bindings of this Result.  # noqa: E501
        :type node_bindings: Dict[str, List[NodeBinding]]
        :param edge_bindings: The edge_bindings of this Result.  # noqa: E501
        :type edge_bindings: Dict[str, List[EdgeBinding]]
        :param id: The id of this Result.  # noqa: E501
        :type id: str
        :param description: The description of this Result.  # noqa: E501
        :type description: str
        :param essence: The essence of this Result.  # noqa: E501
        :type essence: str
        :param essence_category: The essence_category of this Result.  # noqa: E501
        :type essence_category: str
        :param row_data: The row_data of this Result.  # noqa: E501
        :type row_data: List[AnyType]
        :param score: The score of this Result.  # noqa: E501
        :type score: float
        :param score_name: The score_name of this Result.  # noqa: E501
        :type score_name: str
        :param score_direction: The score_direction of this Result.  # noqa: E501
        :type score_direction: str
        :param confidence: The confidence of this Result.  # noqa: E501
        :type confidence: float
        :param result_group: The result_group of this Result.  # noqa: E501
        :type result_group: int
        :param result_group_similarity_score: The result_group_similarity_score of this Result.  # noqa: E501
        :type result_group_similarity_score: float
        :param reasoner_id: The reasoner_id of this Result.  # noqa: E501
        :type reasoner_id: str
        """
        self.openapi_types = {
            'node_bindings': Dict[str, List[NodeBinding]],
            'edge_bindings': Dict[str, List[EdgeBinding]],
            'id': str,
            'description': str,
            'essence': str,
            'essence_category': str,
            'row_data': List[AnyType],
            'score': float,
            'score_name': str,
            'score_direction': str,
            'confidence': float,
            'result_group': int,
            'result_group_similarity_score': float,
            'reasoner_id': str
        }

        self.attribute_map = {
            'node_bindings': 'node_bindings',
            'edge_bindings': 'edge_bindings',
            'id': 'id',
            'description': 'description',
            'essence': 'essence',
            'essence_category': 'essence_category',
            'row_data': 'row_data',
            'score': 'score',
            'score_name': 'score_name',
            'score_direction': 'score_direction',
            'confidence': 'confidence',
            'result_group': 'result_group',
            'result_group_similarity_score': 'result_group_similarity_score',
            'reasoner_id': 'reasoner_id'
        }

        self._node_bindings = node_bindings
        self._edge_bindings = edge_bindings
        self._id = id
        self._description = description
        self._essence = essence
        self._essence_category = essence_category
        self._row_data = row_data
        self._score = score
        self._score_name = score_name
        self._score_direction = score_direction
        self._confidence = confidence
        self._result_group = result_group
        self._result_group_similarity_score = result_group_similarity_score
        self._reasoner_id = reasoner_id

    @classmethod
    def from_dict(cls, dikt) -> 'Result':
        """Returns the dict as a model

        :param dikt: A dict.
        :type: dict
        :return: The Result of this Result.  # noqa: E501
        :rtype: Result
        """
        return util.deserialize_model(dikt, cls)

    @property
    def node_bindings(self):
        """Gets the node_bindings of this Result.

        The dictionary of Input Query Graph to Result Knowledge Graph node bindings where the dictionary keys are the key identifiers of the Query Graph nodes and the associated values of those keys are instances of NodeBinding schema type (see below). This value is an array of NodeBindings since a given query node may have multiple knowledge graph Node bindings in the result.  # noqa: E501

        :return: The node_bindings of this Result.
        :rtype: Dict[str, List[NodeBinding]]
        """
        return self._node_bindings

    @node_bindings.setter
    def node_bindings(self, node_bindings):
        """Sets the node_bindings of this Result.

        The dictionary of Input Query Graph to Result Knowledge Graph node bindings where the dictionary keys are the key identifiers of the Query Graph nodes and the associated values of those keys are instances of NodeBinding schema type (see below). This value is an array of NodeBindings since a given query node may have multiple knowledge graph Node bindings in the result.  # noqa: E501

        :param node_bindings: The node_bindings of this Result.
        :type node_bindings: Dict[str, List[NodeBinding]]
        """
        if node_bindings is None:
            raise ValueError("Invalid value for `node_bindings`, must not be `None`")  # noqa: E501

        self._node_bindings = node_bindings

    @property
    def edge_bindings(self):
        """Gets the edge_bindings of this Result.

        The dictionary of Input Query Graph to Result Knowledge Graph edge bindings where the dictionary keys are the key identifiers of the Query Graph edges and the associated values of those keys are instances of EdgeBinding schema type (see below). This value is an array of EdgeBindings since a given query edge may resolve to multiple knowledge graph edges in the result.  # noqa: E501

        :return: The edge_bindings of this Result.
        :rtype: Dict[str, List[EdgeBinding]]
        """
        return self._edge_bindings

    @edge_bindings.setter
    def edge_bindings(self, edge_bindings):
        """Sets the edge_bindings of this Result.

        The dictionary of Input Query Graph to Result Knowledge Graph edge bindings where the dictionary keys are the key identifiers of the Query Graph edges and the associated values of those keys are instances of EdgeBinding schema type (see below). This value is an array of EdgeBindings since a given query edge may resolve to multiple knowledge graph edges in the result.  # noqa: E501

        :param edge_bindings: The edge_bindings of this Result.
        :type edge_bindings: Dict[str, List[EdgeBinding]]
        """
        if edge_bindings is None:
            raise ValueError("Invalid value for `edge_bindings`, must not be `None`")  # noqa: E501

        self._edge_bindings = edge_bindings

    @property
    def id(self):
        """Gets the id of this Result.

        URI for this result  # noqa: E501

        :return: The id of this Result.
        :rtype: str
        """
        return self._id

    @id.setter
    def id(self, id):
        """Sets the id of this Result.

        URI for this result  # noqa: E501

        :param id: The id of this Result.
        :type id: str
        """

        self._id = id

    @property
    def description(self):
        """Gets the description of this Result.

        A free text description of this result answer from the reasoner  # noqa: E501

        :return: The description of this Result.
        :rtype: str
        """
        return self._description

    @description.setter
    def description(self, description):
        """Sets the description of this Result.

        A free text description of this result answer from the reasoner  # noqa: E501

        :param description: The description of this Result.
        :type description: str
        """

        self._description = description

    @property
    def essence(self):
        """Gets the essence of this Result.

        A single string that is the terse essence of the result (useful for simple answers)  # noqa: E501

        :return: The essence of this Result.
        :rtype: str
        """
        return self._essence

    @essence.setter
    def essence(self, essence):
        """Sets the essence of this Result.

        A single string that is the terse essence of the result (useful for simple answers)  # noqa: E501

        :param essence: The essence of this Result.
        :type essence: str
        """

        self._essence = essence

    @property
    def essence_category(self):
        """Gets the essence_category of this Result.

        A Translator BioLink bioentity category of the essence  # noqa: E501

        :return: The essence_category of this Result.
        :rtype: str
        """
        return self._essence_category

    @essence_category.setter
    def essence_category(self, essence_category):
        """Sets the essence_category of this Result.

        A Translator BioLink bioentity category of the essence  # noqa: E501

        :param essence_category: The essence_category of this Result.
        :type essence_category: str
        """

        self._essence_category = essence_category

    @property
    def row_data(self):
        """Gets the row_data of this Result.

        An arbitrary list of values that captures the essence of the result that can be turned into a tabular result across all answers (each result is a row) for a user that wants simplified tabular output  # noqa: E501

        :return: The row_data of this Result.
        :rtype: List[AnyType]
        """
        return self._row_data

    @row_data.setter
    def row_data(self, row_data):
        """Sets the row_data of this Result.

        An arbitrary list of values that captures the essence of the result that can be turned into a tabular result across all answers (each result is a row) for a user that wants simplified tabular output  # noqa: E501

        :param row_data: The row_data of this Result.
        :type row_data: List[AnyType]
        """

        self._row_data = row_data

    @property
    def score(self):
        """Gets the score of this Result.

        A numerical score associated with this result indicating the relevance or confidence of this result relative to others in the returned set. Higher MUST be better.  # noqa: E501

        :return: The score of this Result.
        :rtype: float
        """
        return self._score

    @score.setter
    def score(self, score):
        """Sets the score of this Result.

        A numerical score associated with this result indicating the relevance or confidence of this result relative to others in the returned set. Higher MUST be better.  # noqa: E501

        :param score: The score of this Result.
        :type score: float
        """

        self._score = score

    @property
    def score_name(self):
        """Gets the score_name of this Result.

        Name for the score  # noqa: E501

        :return: The score_name of this Result.
        :rtype: str
        """
        return self._score_name

    @score_name.setter
    def score_name(self, score_name):
        """Sets the score_name of this Result.

        Name for the score  # noqa: E501

        :param score_name: The score_name of this Result.
        :type score_name: str
        """

        self._score_name = score_name

    @property
    def score_direction(self):
        """Gets the score_direction of this Result.

        Sorting indicator for the score: one of higher_is_better or lower_is_better  # noqa: E501

        :return: The score_direction of this Result.
        :rtype: str
        """
        return self._score_direction

    @score_direction.setter
    def score_direction(self, score_direction):
        """Sets the score_direction of this Result.

        Sorting indicator for the score: one of higher_is_better or lower_is_better  # noqa: E501

        :param score_direction: The score_direction of this Result.
        :type score_direction: str
        """

        self._score_direction = score_direction

    @property
    def confidence(self):
        """Gets the confidence of this Result.

        Confidence metric for this result, a value between (inclusive)  0.0 (no confidence) and 1.0 (highest confidence)  # noqa: E501

        :return: The confidence of this Result.
        :rtype: float
        """
        return self._confidence

    @confidence.setter
    def confidence(self, confidence):
        """Sets the confidence of this Result.

        Confidence metric for this result, a value between (inclusive)  0.0 (no confidence) and 1.0 (highest confidence)  # noqa: E501

        :param confidence: The confidence of this Result.
        :type confidence: float
        """

        self._confidence = confidence

    @property
    def result_group(self):
        """Gets the result_group of this Result.

        An integer group number for results for use in cases where several results should be grouped together. Also useful to control sorting ascending.  # noqa: E501

        :return: The result_group of this Result.
        :rtype: int
        """
        return self._result_group

    @result_group.setter
    def result_group(self, result_group):
        """Sets the result_group of this Result.

        An integer group number for results for use in cases where several results should be grouped together. Also useful to control sorting ascending.  # noqa: E501

        :param result_group: The result_group of this Result.
        :type result_group: int
        """

        self._result_group = result_group

    @property
    def result_group_similarity_score(self):
        """Gets the result_group_similarity_score of this Result.

        A score that denotes the similarity of this result to other members of the result_group  # noqa: E501

        :return: The result_group_similarity_score of this Result.
        :rtype: float
        """
        return self._result_group_similarity_score

    @result_group_similarity_score.setter
    def result_group_similarity_score(self, result_group_similarity_score):
        """Sets the result_group_similarity_score of this Result.

        A score that denotes the similarity of this result to other members of the result_group  # noqa: E501

        :param result_group_similarity_score: The result_group_similarity_score of this Result.
        :type result_group_similarity_score: float
        """

        self._result_group_similarity_score = result_group_similarity_score

    @property
    def reasoner_id(self):
        """Gets the reasoner_id of this Result.

        Identifier string of the reasoner that provided this result (e.g., ARAX, Robokop, etc.)  # noqa: E501

        :return: The reasoner_id of this Result.
        :rtype: str
        """
        return self._reasoner_id

    @reasoner_id.setter
    def reasoner_id(self, reasoner_id):
        """Sets the reasoner_id of this Result.

        Identifier string of the reasoner that provided this result (e.g., ARAX, Robokop, etc.)  # noqa: E501

        :param reasoner_id: The reasoner_id of this Result.
        :type reasoner_id: str
        """

        self._reasoner_id = reasoner_id
