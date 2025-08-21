from __future__ import annotations
import networkx as nx
import re
import math
from typing import List, Optional, Tuple, Dict, Any
from uuid import UUID

from udmm2.memory.models import Concept, Rule, SemanticLink

class SemanticMemory:
    """
    A graph-based semantic memory that stores concepts and rules as nodes
    and the relationships between them as edges.
    """
    def __init__(self):
        self.graph = nx.DiGraph()

    # --- Private Helpers ---
    def _find_node_by_label(self, label: str) -> Optional[UUID]:
        for node_id, data in self.graph.nodes(data=True):
            if isinstance(data.get("data"), Concept) and data["data"].label.lower() == label.lower():
                return node_id
        return None

    def _export_concept(self, concept_id: UUID) -> Optional[Dict[str, Any]]:
        if not self.graph.has_node(concept_id):
            return None

        node = self.graph.nodes[concept_id]
        concept_data: Concept = node["data"]

        relations = []
        for _, target_id, edge_data in self.graph.out_edges(concept_id, data=True):
            relations.append({"relation": edge_data.get("type", "associates"), "target_id": str(target_id)})

        return concept_data.model_dump(exclude={'id'}) | {'id': concept_id, 'relations': relations}

    def _export_rule(self, rule_id: UUID) -> Optional[Dict[str, Any]]:
        if not self.graph.has_node(rule_id):
            return None
        rule_data: Rule = self.graph.nodes[rule_id]["data"]
        dump = rule_data.model_dump()
        # Remap aliased fields for the API output
        dump['conditions'] = dump.pop('if_')
        dump['actions'] = dump.pop('then')
        return dump

    # --- Public Methods ---
    def add_concept(self, label: str, description: str, attributes: dict, relations: list, confidence: float = 0.95) -> UUID:
        concept = Concept(label=label, description=description, attributes=attributes, confidence=confidence)
        self.graph.add_node(concept.id, data=concept, type="concept")

        for rel in relations:
            target_id = UUID(rel.get("target_id"))
            if self.graph.has_node(target_id):
                link = SemanticLink(source=concept.id, target=target_id, type=rel.get("relation", "associates"))
                self.graph.add_edge(link.source, link.target, type=link.type, weight=link.weight)
        return concept.id

    def get_concept_by_id(self, concept_id: UUID) -> Optional[Dict[str, Any]]:
        return self._export_concept(concept_id)

    def update_concept(self, concept_id: UUID, patch: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if not self.graph.has_node(concept_id) or not isinstance(self.graph.nodes[concept_id].get("data"), Concept):
            return None

        node_data = self.graph.nodes[concept_id]["data"]
        updated_data = node_data.model_copy(update=patch)
        self.graph.nodes[concept_id]["data"] = updated_data
        return self._export_concept(concept_id)

    def add_rule(self, conditions: list, actions: list, priority: int, confidence: float, source: str) -> UUID:
        rule = Rule(if_=conditions, then=actions, priority=priority, confidence=confidence, source=source)
        self.graph.add_node(rule.id, data=rule, type="rule")

        # Automatically link rule to concepts in its conditions
        for cond in conditions:
            # Simple regex to find concept labels, e.g., "concept('Heat')"
            match = re.search(r"concept\('([^']+)'\)", cond)
            if match:
                concept_label = match.group(1)
                concept_id = self._find_node_by_label(concept_label)
                if concept_id:
                    link = SemanticLink(source=rule.id, target=concept_id, type="applies_to")
                    self.graph.add_edge(link.source, link.target, type=link.type, weight=link.weight)
        return rule.id

    def get_rule_by_id(self, rule_id: UUID) -> Optional[Dict[str, Any]]:
        return self._export_rule(rule_id)

    def rules_related_to_concept(self, concept_id: UUID) -> List[UUID]:
        related_rules = []
        if self.graph.has_node(concept_id):
            # Find rules that link TO this concept
            for predecessor, _, edge_data in self.graph.in_edges(concept_id, data=True):
                if self.graph.nodes[predecessor].get("type") == "rule" and edge_data.get("type") == "applies_to":
                    related_rules.append(predecessor)
        return list(set(related_rules))

    def get_related(self, concept_name: str) -> List[str]:
        concept_id = self._find_node_by_label(concept_name)
        if not concept_id: return []

        related_labels = []
        for _, target_id, _ in self.graph.out_edges(concept_id, data=True):
            node_data = self.graph.nodes[target_id].get("data")
            if isinstance(node_data, Concept):
                related_labels.append(node_data.label)
        return related_labels

    def get_attributes(self, concept_name: str) -> Dict[str, str]:
        concept_id = self._find_node_by_label(concept_name)
        if concept_id:
            node_data = self.graph.nodes[concept_id].get("data")
            if isinstance(node_data, Concept):
                return node_data.attributes
        return {}

    def query_related(self, node_id: UUID) -> List[Tuple[UUID, float]]:
        if not self.graph.has_node(node_id): return []

        related_nodes = []
        for _, successor, data in self.graph.out_edges(node_id, data=True):
            related_nodes.append((successor, data.get("weight", 0.0)))
        return related_nodes

    def search_labels_in_string(self, text: str) -> List[str]:
        """Finds all known concept labels mentioned in a given string."""
        found_labels = []
        # This is a simple implementation; a real one would use more advanced NLP
        for node_id, data in self.graph.nodes(data=True):
            if isinstance(data.get("data"), Concept):
                if re.search(r'\b' + re.escape(data["data"].label) + r'\b', text, re.IGNORECASE):
                    found_labels.append(data["data"].label)
        return list(set(found_labels))

    def rules_related_to_label(self, label: str) -> List[UUID]:
        """Finds all rules related to a concept label."""
        concept_id = self._find_node_by_label(label)
        if concept_id:
            return self.rules_related_to_concept(concept_id)
        return []

    def set_rule_confidence(self, rule_id: UUID, new_conf: float) -> bool:
        """Updates the confidence of a specific rule."""
        if self.graph.has_node(rule_id) and isinstance(self.graph.nodes[rule_id].get("data"), Rule):
            self.graph.nodes[rule_id]["data"].confidence = new_conf
            return True
        return False

    def closest_concept(self, x: float, y: float) -> Optional[str]:
        """Finds the label of the concept closest to the given (x, y) coordinates."""
        min_dist = float('inf')
        closest_label = None

        for node_id, data in self.graph.nodes(data=True):
            node_data = data.get("data")
            if isinstance(node_data, Concept):
                attrs = node_data.attributes
                if isinstance(attrs, dict) and "x" in attrs and "y" in attrs:
                    cx, cy = float(attrs["x"]), float(attrs["y"])
                    dist = math.hypot(cx - x, cy - y)
                    if dist < min_dist:
                        min_dist = dist
                        closest_label = node_data.label

        return closest_label

    def get_graph_data(self) -> Dict[str, List[Dict[str, Any]]]:
        """Returns a serializable representation of the graph for visualization."""
        nodes = []
        for node_id, data in self.graph.nodes(data=True):
            node_obj = data.get("data")
            if isinstance(node_obj, Concept):
                nodes.append({
                    "id": str(node_id),
                    "label": node_obj.label,
                    "title": node_obj.description,
                    "type": "concept"
                })
            elif isinstance(node_obj, Rule):
                nodes.append({
                    "id": str(node_id),
                    "label": f"Rule {str(node_id)[:4]}",
                    "title": f"IF {node_obj.if_} THEN {node_obj.then}",
                    "type": "rule"
                })

        edges = []
        for source, target, data in self.graph.edges(data=True):
            edges.append({
                "source": str(source),
                "target": str(target),
                "label": data.get("type", "related")
            })

        return {"nodes": nodes, "edges": edges}
