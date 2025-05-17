"""
Monitors and analyzes discussions between expert agents to determine consensus
and track convergence of opinions.
"""

from typing import Dict, List, Set
from dataclasses import dataclass
from datetime import datetime

@dataclass
class ConsensusMetrics:
    """Metrics for measuring consensus in discussions"""
    agreement_score: float
    disagreement_points: List[str]
    resolved_points: List[str]
    unresolved_points: List[str]

class DiscussionMonitor:
    def __init__(self):
        self.consensus_threshold = 0.8  # 80% agreement needed for consensus
        self.min_expert_participation = 0.8  # At least 80% of experts must participate
        self.key_points_cache = {}
        
    def check_consensus(self, discussion_history: List[Dict]) -> bool:
        """Check if consensus has been reached in the discussion"""
        if not discussion_history:
            return False
            
        # Get latest round of discussion
        latest_round = self._get_latest_round(discussion_history)
        if not latest_round:
            return False
            
        # Calculate consensus metrics
        metrics = self._calculate_consensus_metrics(latest_round)
        
        # Check if we have sufficient participation
        if not self._check_participation(latest_round):
            return False
            
        # Check if we've reached consensus threshold
        return metrics.agreement_score >= self.consensus_threshold
        
    def check_convergence(self, discussion_history: List[Dict]) -> bool:
        """Check if opinions are converging over discussion rounds"""
        if len(discussion_history) < 2:
            return False
            
        # Get discussion rounds
        rounds = self._group_by_rounds(discussion_history)
        if len(rounds) < 2:
            return False
            
        # Calculate convergence between last two rounds
        last_round = rounds[-1]
        previous_round = rounds[-2]
        
        convergence_score = self._calculate_convergence(previous_round, last_round)
        return convergence_score >= self.consensus_threshold
        
    def _calculate_consensus_metrics(self, round_contributions: List[Dict]) -> ConsensusMetrics:
        """Calculate detailed metrics about consensus level"""
        # Extract key points from each contribution
        all_points = set()
        point_agreements = {}
        
        for contrib in round_contributions:
            points = self._extract_key_points(contrib["content"])
            for point in points:
                if point not in point_agreements:
                    point_agreements[point] = 0
                point_agreements[point] += 1
                all_points.add(point)
        
        # Calculate agreement scores
        total_experts = len(round_contributions)
        agreement_scores = {
            point: count/total_experts 
            for point, count in point_agreements.items()
        }
        
        # Classify points
        disagreement_points = []
        resolved_points = []
        unresolved_points = []
        
        for point, score in agreement_scores.items():
            if score < 0.5:  # Less than 50% agreement
                disagreement_points.append(point)
            elif score >= self.consensus_threshold:
                resolved_points.append(point)
            else:
                unresolved_points.append(point)
        
        # Calculate overall agreement score
        if resolved_points:
            agreement_score = len(resolved_points) / len(all_points)
        else:
            agreement_score = 0
            
        return ConsensusMetrics(
            agreement_score=agreement_score,
            disagreement_points=disagreement_points,
            resolved_points=resolved_points,
            unresolved_points=unresolved_points
        )
        
    def _calculate_convergence(self, previous_round: List[Dict], current_round: List[Dict]) -> float:
        """Calculate how much opinions have converged between rounds"""
        # Get key points from each round
        previous_points = self._get_round_key_points(previous_round)
        current_points = self._get_round_key_points(current_round)
        
        # Calculate similarity between rounds
        common_points = previous_points.intersection(current_points)
        all_points = previous_points.union(current_points)
        
        if not all_points:
            return 0
            
        return len(common_points) / len(all_points)
        
    def _get_round_key_points(self, round_contributions: List[Dict]) -> Set[str]:
        """Get set of key points from a round of contributions"""
        points = set()
        for contrib in round_contributions:
            points.update(self._extract_key_points(contrib["content"]))
        return points
        
    def _extract_key_points(self, content: Dict) -> List[str]:
        """Extract key points from a contribution's content"""
        # Check cache first
        content_str = str(content)
        if content_str in self.key_points_cache:
            return self.key_points_cache[content_str]
            
        # Extract points based on content structure
        points = []
        
        if isinstance(content, dict):
            # Extract from known fields
            if "concerns" in content:
                points.extend([c["description"] if isinstance(c, dict) else c 
                             for c in content.get("concerns", [])])
                
            if "recommendations" in content:
                points.extend([r["description"] if isinstance(r, dict) else r 
                             for r in content.get("recommendations", [])])
                
            # Extract from analysis text if present
            if "analysis" in content:
                analysis = content["analysis"]
                if isinstance(analysis, dict) and "text" in analysis:
                    points.extend(self._extract_points_from_text(analysis["text"]))
                elif isinstance(analysis, str):
                    points.extend(self._extract_points_from_text(analysis))
        
        # Cache results
        self.key_points_cache[content_str] = points
        return points

    def _extract_points_from_text(self, text: str) -> List[str]:
        """Extract key points from text content"""
        if not isinstance(text, str):
            return []
            
        # Simple extraction of bullet points or numbered lists
        points = []
        current_point = []
        
        for line in text.split('\n'):
            line = line.strip()
            if not line:
                continue
                
            # Check for bullet points or numbers
            if line[0] in ['•', '-', '*'] or (line[0].isdigit() and '. ' in line):
                if current_point:
                    points.append(' '.join(current_point))
                    current_point = []
                if line[0].isdigit():
                    point_text = line.split('. ', 1)[1]
                else:
                    point_text = line[1:].strip()
                current_point.append(point_text)
            else:
                current_point.append(line)
        
        if current_point:
            points.append(' '.join(current_point))
            
        return points
        
    def _get_latest_round(self, discussion_history: List[Dict]) -> List[Dict]:
        """Get contributions from the latest discussion round"""
        if not discussion_history:
            return []
            
        # Group by rounds
        rounds = self._group_by_rounds(discussion_history)
        return rounds[-1] if rounds else []
        
    def _group_by_rounds(self, discussion_history: List[Dict]) -> List[List[Dict]]:
        """Group discussion contributions by rounds"""
        rounds = {}
        
        for contrib in discussion_history:
            if contrib["type"] == "discussion":
                round_num = contrib["round"]
                if round_num not in rounds:
                    rounds[round_num] = []
                rounds[round_num].append(contrib)
        
        return [rounds[key] for key in sorted(rounds.keys())]
        
    def _check_participation(self, round_contributions: List[Dict]) -> bool:
        """Check if we have sufficient expert participation"""
        unique_experts = len({contrib["agent"] for contrib in round_contributions})
        return unique_experts >= 5 * self.min_expert_participation  # 5 total experts