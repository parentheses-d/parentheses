from typing import Dict, List, Tuple
import asyncio
import json
import numpy as np
from datetime import datetime
import logging


class LearningPathway:
    def __init__(self, domain: str):
        self.domain = domain
        self.knowledge_graph: Dict[str, dict] = {}
        self.connections: Dict[str, List[str]] = {}
        self.performance_metrics: Dict[str, float] = {}
        self.contributor_scores: Dict[str, float] = {}
        self.logger = logging.getLogger(__name__)

    async def add_knowledge(self, knowledge_id: str, knowledge_data: dict):
        try:
            self.knowledge_graph[knowledge_id] = knowledge_data

            # Update connections
            related_ids = self._find_related_knowledge(knowledge_data)
            self.connections[knowledge_id] = related_ids

            # Update bidirectional connections
            for related_id in related_ids:
                if related_id in self.connections:
                    self.connections[related_id].append(knowledge_id)

            # Update contributor score
            contributor = knowledge_data.get('contributor')
            if contributor:
                current_score = self.contributor_scores.get(contributor, 0)
                self.contributor_scores[contributor] = current_score + 1

            await self._calculate_performance_metrics(knowledge_id)
        except Exception as e:
            self.logger.error(f"Failed to add knowledge: {str(e)}")
            raise

    async def query_knowledge(self, query_params: dict) -> List[dict]:
        try:
            matched_knowledge = []
            for knowledge_id, knowledge_data in self.knowledge_graph.items():
                if self._matches_query(knowledge_data, query_params):
                    matched_knowledge.append({
                        **knowledge_data,
                        'performance_score': self.performance_metrics.get(knowledge_id, 0)
                    })

            # Sort by performance score
            matched_knowledge.sort(
                key=lambda x: x['performance_score'],
                reverse=True
            )

            return matched_knowledge
        except Exception as e:
            self.logger.error(f"Failed to query knowledge: {str(e)}")
            raise

    async def optimize_pathways(self):
        try:
            # Calculate centrality for each knowledge node
            centrality_scores = self._calculate_centrality()

            # Update performance metrics based on centrality
            for knowledge_id, centrality in centrality_scores.items():
                current_performance = self.performance_metrics.get(knowledge_id, 0)
                self.performance_metrics[knowledge_id] = (
                        0.7 * current_performance + 0.3 * centrality
                )

            # Prune low-performing connections
            await self._prune_connections()
        except Exception as e:
            self.logger.error(f"Failed to optimize pathways: {str(e)}")

    async def get_top_contributors(self) -> List[Tuple[str, float]]:
        try:
            contributors = list(self.contributor_scores.items())
            contributors.sort(key=lambda x: x[1], reverse=True)
            return contributors[:10]  # Return top 10 contributors
        except Exception as e:
            self.logger.error(f"Failed to get top contributors: {str(e)}")
            return []

    def _find_related_knowledge(self, knowledge_data: dict) -> List[str]:
        related = []
        for existing_id, existing_data in self.knowledge_graph.items():
            if self._calculate_similarity(knowledge_data, existing_data) > 0.7:
                related.append(existing_id)
        return related

    def _calculate_similarity(self, data1: dict, data2: dict) -> float:
        text1 = json.dumps(data1.get('content', ''))
        text2 = json.dumps(data2.get('content', ''))

        # Simple Jaccard similarity
        set1 = set(text1.split())
        set2 = set(text2.split())

        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))

        return intersection / union if union > 0 else 0

    def _calculate_centrality(self) -> Dict[str, float]:
        matrix_size = len(self.knowledge_graph)
        if matrix_size == 0:
            return {}

        # Create adjacency matrix
        adjacency_matrix = np.zeros((matrix_size, matrix_size))
        id_to_index = {id_: i for i, id_ in enumerate(self.knowledge_graph.keys())}

        for id_, connections in self.connections.items():
            for connected_id in connections:
                i = id_to_index[id_]
                j = id_to_index[connected_id]
                adjacency_matrix[i, j] = 1

        # Calculate eigenvector centrality
        eigenvalues, eigenvectors = np.linalg.eig(adjacency_matrix.T)
        centrality_vector = eigenvectors[:, eigenvalues.argmax()].real

        # Normalize and convert to dictionary
        centrality_vector = centrality_vector / centrality_vector.sum()
        return {
            id_: centrality_vector[i]
            for id_, i in id_to_index.items()
        }

    async def _calculate_performance_metrics(self, knowledge_id: str):
        try:
            knowledge_data = self.knowledge_graph[knowledge_id]

            # Calculate base score from metadata
            timestamp = datetime.fromisoformat(knowledge_data.get('timestamp', ''))
            age_factor = 1 / (1 + (datetime.now() - timestamp).days)

            # Calculate usage score
            usage_count = knowledge_data.get('usage_count', 0)
            usage_factor = np.log1p(usage_count)

            # Combine scores
            self.performance_metrics[knowledge_id] = (
                    0.4 * age_factor + 0.6 * usage_factor
            )
        except Exception as e:
            self.logger.error(f"Failed to calculate performance metrics: {str(e)}")

    def _matches_query(self, knowledge_data: dict, query_params: dict) -> bool:
        for key, value in query_params.items():
            if key not in knowledge_data or knowledge_data[key] != value:
                return False
        return True

    async def _prune_connections(self):
        threshold = np.mean(list(self.performance_metrics.values()))

        pruned_connections = {}
        for knowledge_id, connections in self.connections.items():
            pruned_connections[knowledge_id] = [
                conn_id for conn_id in connections
                if self.performance_metrics.get(conn_id, 0) >= threshold
            ]

        self.connections = pruned_connections