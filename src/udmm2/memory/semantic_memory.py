import networkx as nx
from typing import List, Optional, Tuple

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
