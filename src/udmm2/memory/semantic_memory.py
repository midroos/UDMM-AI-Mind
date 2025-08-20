import networkx as nx
from typing import List, Optional, Tuple, Dict

from udmm2.memory.models import Concept, Rule, SemanticLink

class SemanticMemory:
    """
    A graph-based semantic memory that stores concepts and rules as nodes
    and the relationships between them as edges.
    """

    def __init__(self):
        """Initializes the semantic memory graph."""
        self.graph = nx.DiGraph()

    def add_concept(self, concept: Concept) -> None:
        """
        Adds a concept to the memory graph.

        Args:
            concept: The Concept object to add.
        """
        self.graph.add_node(concept.id, data=concept, type="concept")

    def add_rule(self, rule: Rule) -> None:
        """
        Adds a rule to the memory graph.

        Args:
            rule: The Rule object to add.
        """
        self.graph.add_node(rule.id, data=rule, type="rule")

    def get_node_data(self, node_id: str) -> Optional[Concept | Rule]:
        """
        Retrieves the data object for a given node.

        Args:
            node_id: The ID of the node to retrieve.

        Returns:
            The Concept or Rule object, or None if not found.
        """
        if self.graph.has_node(node_id):
            return self.graph.nodes[node_id].get("data")
        return None

    def link_nodes(self, link: SemanticLink) -> None:
        """
        Creates a directed, weighted link between two nodes.

        Args:
            link: A SemanticLink object describing the connection.
        """
        if self.graph.has_node(link.source) and self.graph.has_node(link.target):
            self.graph.add_edge(
                link.source,
                link.target,
                type=link.type,
                weight=link.weight,
            )

    def query_related(
        self, concept_id: str, relation_type: Optional[str] = None
    ) -> List[Tuple[str, float]]:
        """
        Finds all nodes connected to a given concept by an outgoing edge,
        optionally filtering by relation type.

        Args:
            concept_id: The ID of the starting concept node.
            relation_type: If specified, only returns neighbors connected by this
                           type of edge.

        Returns:
            A list of tuples, where each tuple contains the ID of a related
            node and the weight of the connecting edge.
        """
        if not self.graph.has_node(concept_id):
            return []

        related_nodes = []
        for successor in self.graph.successors(concept_id):
            edge_data = self.graph.get_edge_data(concept_id, successor)
            if relation_type is None or edge_data.get("type") == relation_type:
                weight = edge_data.get("weight", 0.0)
                related_nodes.append((successor, weight))

        return related_nodes

    def _find_node_by_label(self, label: str) -> Optional[str]:
        """Finds the first node ID with a matching label."""
        for node_id, data in self.graph.nodes(data=True):
            if data.get("data") and data["data"].label == label:
                return node_id
        return None

    def add_concept_simple(self, name: str, attributes: Dict[str, str], related: List[str]):
        """
        A simple way to add a concept and its relations.
        This is a convenience method for testing and simple cases.
        """
        # Create or find the main concept
        main_concept_id = self._find_node_by_label(name)
        if not main_concept_id:
            main_concept = Concept(id=name, label=name, attributes=attributes)
            self.add_concept(main_concept)
            main_concept_id = name

        # Create or find related concepts and link them
        for related_name in related:
            related_concept_id = self._find_node_by_label(related_name)
            if not related_concept_id:
                related_concept = Concept(id=related_name, label=related_name)
                self.add_concept(related_concept)
                related_concept_id = related_name

            link = SemanticLink(source=main_concept_id, target=related_concept_id, type="related_to", weight=0.5)
            self.link_nodes(link)

    def get_related(self, concept_name: str) -> List[str]:
        """
        Gets the labels of all concepts related to the given concept name.
        """
        concept_id = self._find_node_by_label(concept_name)
        if not concept_id:
            return []

        related_ids = [succ for succ, _ in self.query_related(concept_id)]
        related_labels = []
        for rid in related_ids:
            node_data = self.get_node_data(rid)
            if node_data:
                related_labels.append(node_data.label)
        return related_labels

    def get_attributes(self, concept_name: str) -> Dict[str, str]:
        """
        Gets the attributes of a concept by its name.
        """
        concept_id = self._find_node_by_label(concept_name)
        if concept_id:
            node_data = self.get_node_data(concept_id)
            if node_data and isinstance(node_data, Concept):
                return node_data.attributes
        return {}
