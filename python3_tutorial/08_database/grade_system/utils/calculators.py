from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class GradeWeights:
    """Grade component weights"""
    midterm: float = 0.3
    final: float = 0.4
    assignment: float = 0.2
    attendance: float = 0.1
    
    def validate(self) -> bool:
        """Validate that weights sum to 1.0"""
        total = self.midterm + self.final + self.assignment + self.attendance
        if abs(total - 1.0) > 0.001:
            raise ValueError(f"Weights must sum to 1.0, got {total}")
        return True


class GradeCalculator:
    """Calculator for grade-related computations"""
    
    # Grade scale mapping
    GRADE_SCALE = [
        (95, "A+", 4.5),
        (90, "A0", 4.0),
        (85, "A-", 3.5),
        (80, "B+", 3.0),
        (75, "B0", 2.5),
        (70, "B-", 2.0),
        (65, "C+", 1.5),
        (60, "C0", 1.0),
        (55, "C-", 0.5),
        (0,  "F",  0.0)
    ]
    
    def __init__(self, weights: Optional[GradeWeights] = None):
        self.weights = weights or GradeWeights()
        self.weights.validate()
        
    def calculate_total_score(self,
                            midterm: Optional[float] = None,
                            final: Optional[float] = None,
                            assignment: Optional[float] = None,
                            attendance: Optional[float] = None) -> float:
        """Calculate total score from components"""
        total = 0.0
        
        if midterm is not None:
            total += midterm * self.weights.midterm
        if final is not None:
            total += final * self.weights.final
        if assignment is not None:
            total += assignment * self.weights.assignment
        if attendance is not None:
            total += attendance * self.weights.attendance
            
        return round(total, 2)
        
    def score_to_letter_grade(self, score: float) -> Tuple[str, float]:
        """Convert numerical score to letter grade and grade points"""
        for min_score, letter, points in self.GRADE_SCALE:
            if score >= min_score:
                return letter, points
        return "F", 0.0
        
    def letter_grade_to_points(self, letter_grade: str) -> float:
        """Convert letter grade to grade points"""
        for _, letter, points in self.GRADE_SCALE:
            if letter == letter_grade:
                return points
        raise ValueError(f"Invalid letter grade: {letter_grade}")
        
    def calculate_gpa(self, grades: List[Tuple[float, int]]) -> float:
        """
        Calculate GPA from list of (grade_points, credits) tuples
        
        Args:
            grades: List of tuples containing (grade_points, credits)
            
        Returns:
            Calculated GPA
        """
        if not grades:
            return 0.0
            
        total_points = sum(points * credits for points, credits in grades)
        total_credits = sum(credits for _, credits in grades)
        
        if total_credits == 0:
            return 0.0
            
        return round(total_points / total_credits, 2)
        
    def calculate_class_average(self, scores: List[float]) -> Dict[str, float]:
        """Calculate class statistics"""
        if not scores:
            return {
                "mean": 0.0,
                "median": 0.0,
                "min": 0.0,
                "max": 0.0,
                "std_dev": 0.0
            }
            
        sorted_scores = sorted(scores)
        n = len(scores)
        
        mean = sum(scores) / n
        median = sorted_scores[n // 2] if n % 2 == 1 else \
                (sorted_scores[n // 2 - 1] + sorted_scores[n // 2]) / 2
                
        # Calculate standard deviation
        variance = sum((x - mean) ** 2 for x in scores) / n
        std_dev = variance ** 0.5
        
        return {
            "mean": round(mean, 2),
            "median": round(median, 2),
            "min": round(min(scores), 2),
            "max": round(max(scores), 2),
            "std_dev": round(std_dev, 2)
        }
        
    def calculate_grade_distribution(self, scores: List[float]) -> Dict[str, int]:
        """Calculate grade distribution for a list of scores"""
        distribution = {}
        
        for score in scores:
            letter_grade, _ = self.score_to_letter_grade(score)
            distribution[letter_grade] = distribution.get(letter_grade, 0) + 1
            
        return distribution
        
    def calculate_percentile(self, score: float, all_scores: List[float]) -> float:
        """Calculate percentile rank of a score"""
        if not all_scores:
            return 0.0
            
        below_count = sum(1 for s in all_scores if s < score)
        equal_count = sum(1 for s in all_scores if s == score)
        
        percentile = (below_count + 0.5 * equal_count) / len(all_scores) * 100
        
        return round(percentile, 2)
        
    def calculate_curved_grade(self, score: float, mean: float, std_dev: float,
                             curve_type: str = "normal") -> float:
        """Apply curve to a grade"""
        if curve_type == "normal":
            # Normal curve: adjust based on standard deviation
            if std_dev == 0:
                return score
                
            z_score = (score - mean) / std_dev
            # Map z-score to grade range (60-100)
            curved = 80 + z_score * 10
            curved = max(0, min(100, curved))
            
        elif curve_type == "linear":
            # Linear curve: add fixed points
            curved = min(100, score + 5)
            
        elif curve_type == "sqrt":
            # Square root curve
            curved = 10 * (score ** 0.5)
            curved = min(100, curved)
            
        else:
            raise ValueError(f"Unknown curve type: {curve_type}")
            
        return round(curved, 2)
        
    def calculate_weighted_average(self, scores: List[Tuple[float, float]]) -> float:
        """
        Calculate weighted average
        
        Args:
            scores: List of (score, weight) tuples
            
        Returns:
            Weighted average
        """
        if not scores:
            return 0.0
            
        total_weighted = sum(score * weight for score, weight in scores)
        total_weight = sum(weight for _, weight in scores)
        
        if total_weight == 0:
            return 0.0
            
        return round(total_weighted / total_weight, 2)
        
    def predict_final_grade(self, current_scores: Dict[str, float],
                          target_grade: str = "B0") -> Dict[str, float]:
        """Predict required scores to achieve target grade"""
        target_score = 0
        for min_score, letter, _ in self.GRADE_SCALE:
            if letter == target_grade:
                target_score = min_score
                break
                
        if target_score == 0:
            raise ValueError(f"Invalid target grade: {target_grade}")
            
        # Calculate current contribution
        current_total = 0
        remaining_weight = 0
        
        if "midterm" in current_scores:
            current_total += current_scores["midterm"] * self.weights.midterm
        else:
            remaining_weight += self.weights.midterm
            
        if "final" in current_scores:
            current_total += current_scores["final"] * self.weights.final
        else:
            remaining_weight += self.weights.final
            
        if "assignment" in current_scores:
            current_total += current_scores["assignment"] * self.weights.assignment
        else:
            remaining_weight += self.weights.assignment
            
        if "attendance" in current_scores:
            current_total += current_scores["attendance"] * self.weights.attendance
        else:
            remaining_weight += self.weights.attendance
            
        # Calculate required score for remaining components
        if remaining_weight > 0:
            required_score = (target_score - current_total) / remaining_weight
            required_score = max(0, min(100, required_score))
        else:
            required_score = 0
            
        return {
            "target_grade": target_grade,
            "target_score": target_score,
            "current_total": round(current_total, 2),
            "required_average": round(required_score, 2),
            "achievable": required_score <= 100
        }