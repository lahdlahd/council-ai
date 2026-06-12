"""
Quantitative Analysis Tools
Pattern recognition, backtesting, probability scoring, correlation analysis

Production-grade with statistical rigor and comprehensive validation
"""

import numpy as np
from typing import List, Dict, Tuple, Optional
from datetime import datetime, timedelta
from enum import Enum
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)


class PatternType(str, Enum):
    """Identified price patterns"""
    MEAN_REVERSION = "mean_reversion"
    MOMENTUM = "momentum"
    BREAKOUT = "breakout"
    PULLBACK = "pullback"
    REVERSAL = "reversal"
    CONSOLIDATION = "consolidation"
    TREND_CONTINUATION = "trend_continuation"


class CorrelationType(str, Enum):
    """Correlation strength classification"""
    VERY_STRONG = "very_strong"      # > 0.8
    STRONG = "strong"                # 0.6 - 0.8
    MODERATE = "moderate"            # 0.4 - 0.6
    WEAK = "weak"                    # 0.2 - 0.4
    VERY_WEAK = "very_weak"          # < 0.2


class QuantTools:
    """Suite of quantitative analysis tools"""
    
    @staticmethod
    def identify_pattern(
        closes: List[float],
        highs: List[float],
        lows: List[float],
        lookback: int = 20
    ) -> Dict[str, any]:
        """
        Identify price patterns in recent candles
        
        Args:
            closes: List of closing prices
            highs: List of high prices
            lows: List of low prices
            lookback: Period to analyze
        
        Returns:
            Dict with pattern type, confidence, description
        """
        try:
            if len(closes) < lookback:
                lookback = len(closes)
            
            closes_arr = np.array(closes[-lookback:], dtype=float)
            highs_arr = np.array(highs[-lookback:], dtype=float)
            lows_arr = np.array(lows[-lookback:], dtype=float)
            
            # Calculate metrics
            sma = np.mean(closes_arr)
            current_price = closes_arr[-1]
            high = np.max(highs_arr)
            low = np.min(lows_arr)
            range_price = high - low
            
            # Distance from SMA
            distance_from_sma = (current_price - sma) / sma
            
            # Volatility
            volatility = np.std(closes_arr) / sma
            
            # Trend
            slope = np.polyfit(np.arange(len(closes_arr)), closes_arr, 1)[0]
            slope_normalized = slope / sma
            
            # Identify pattern
            pattern = PatternType.CONSOLIDATION
            confidence = 0.5
            description = "Consolidation"
            
            # Mean reversion pattern
            if abs(distance_from_sma) > 0.05 and volatility < 0.02:
                pattern = PatternType.MEAN_REVERSION
                confidence = 0.7
                direction = "down" if current_price > sma else "up"
                description = f"Price {distance_from_sma:.1%} from SMA, likely to revert {direction}"
            
            # Momentum pattern
            elif slope_normalized > 0.01 and current_price > sma:
                pattern = PatternType.MOMENTUM
                confidence = 0.75
                description = f"Strong upward momentum with {slope_normalized:.1%} daily slope"
            
            elif slope_normalized < -0.01 and current_price < sma:
                pattern = PatternType.MOMENTUM
                confidence = 0.75
                description = f"Strong downward momentum with {slope_normalized:.1%} daily slope"
            
            # Breakout pattern
            elif current_price > high * 0.98 and slope_normalized > 0:
                pattern = PatternType.BREAKOUT
                confidence = 0.8
                description = f"Breakout above resistance at ${high:.2f}"
            
            elif current_price < low * 1.02 and slope_normalized < 0:
                pattern = PatternType.BREAKOUT
                confidence = 0.8
                description = f"Breakout below support at ${low:.2f}"
            
            # Pullback pattern
            elif slope_normalized > 0 and (current_price < sma):
                pattern = PatternType.PULLBACK
                confidence = 0.65
                description = f"Pullback in uptrend, support at ${sma:.2f}"
            
            elif slope_normalized < 0 and (current_price > sma):
                pattern = PatternType.PULLBACK
                confidence = 0.65
                description = f"Pullback in downtrend, resistance at ${sma:.2f}"
            
            # Reversal pattern
            elif abs(slope_normalized) < 0.002 and volatility > 0.03:
                pattern = PatternType.REVERSAL
                confidence = 0.6
                description = "High volatility with low slope suggests potential reversal"
            
            return {
                "pattern": pattern.value,
                "confidence": float(confidence),
                "description": description,
                "metrics": {
                    "distance_from_sma": float(distance_from_sma),
                    "volatility": float(volatility),
                    "slope": float(slope_normalized)
                }
            }
            
        except Exception as e:
            logger.error(f"Pattern identification failed: {e}")
            return {
                "pattern": PatternType.CONSOLIDATION.value,
                "confidence": 0.3,
                "description": f"Pattern analysis failed: {str(e)}",
                "metrics": {}
            }
    
    @staticmethod
    def calculate_win_rate(
        historical_prices: List[float],
        signal_indicators: List[float],
        threshold: float = 0.5
    ) -> Dict[str, any]:
        """
        Calculate historical win rate based on signal performance
        
        Uses backtesting: If signal > threshold and price went up = win
        
        Args:
            historical_prices: List of historical closing prices
            signal_indicators: Corresponding signal values (0-1)
            threshold: Signal threshold for action
        
        Returns:
            Dict with win_rate, total_signals, wins, losses
        """
        try:
            if len(historical_prices) < 2 or len(signal_indicators) != len(historical_prices):
                return {
                    "win_rate": 0.5,
                    "total_signals": 0,
                    "wins": 0,
                    "losses": 0,
                    "confidence": 0.0
                }
            
            prices_arr = np.array(historical_prices, dtype=float)
            signals_arr = np.array(signal_indicators, dtype=float)
            
            wins = 0
            losses = 0
            
            # Backtest: for each signal > threshold, check if next candle was profitable
            for i in range(len(signals_arr) - 1):
                if signals_arr[i] > threshold:
                    price_return = (prices_arr[i + 1] - prices_arr[i]) / prices_arr[i]
                    if price_return > 0:
                        wins += 1
                    else:
                        losses += 1
            
            total_signals = wins + losses
            
            if total_signals == 0:
                win_rate = 0.5
                confidence = 0.0
            else:
                win_rate = wins / total_signals
                # Confidence increases with sample size (need 30+ for high confidence)
                confidence = min(total_signals / 30, 1.0)
            
            return {
                "win_rate": float(win_rate),
                "total_signals": total_signals,
                "wins": wins,
                "losses": losses,
                "confidence": float(confidence)
            }
            
        except Exception as e:
            logger.error(f"Win rate calculation failed: {e}")
            return {
                "win_rate": 0.5,
                "total_signals": 0,
                "wins": 0,
                "losses": 0,
                "confidence": 0.0
            }
    
    @staticmethod
    def calculate_sharpe_ratio(
        returns: List[float],
        risk_free_rate: float = 0.02,
        periods_per_year: int = 365
    ) -> Dict[str, float]:
        """
        Calculate Sharpe Ratio (risk-adjusted return)
        
        Sharpe = (mean_return - risk_free_rate) / std_dev
        
        Args:
            returns: List of period returns (as decimals, e.g., 0.05 = 5%)
            risk_free_rate: Annual risk-free rate (default 2%)
            periods_per_year: Number of periods in a year (default 365 for daily)
        
        Returns:
            Dict with sharpe_ratio, annualized_return, annualized_volatility
        """
        try:
            if len(returns) < 2:
                return {
                    "sharpe_ratio": 0.0,
                    "annualized_return": 0.0,
                    "annualized_volatility": 0.0
                }
            
            returns_arr = np.array(returns, dtype=float)
            
            # Calculate metrics
            mean_return = np.mean(returns_arr)
            std_dev = np.std(returns_arr)
            
            # Annualize
            annualized_return = mean_return * periods_per_year
            annualized_volatility = std_dev * np.sqrt(periods_per_year)
            
            # Adjust for risk-free rate (annualized)
            excess_return = annualized_return - risk_free_rate
            
            # Sharpe ratio
            if annualized_volatility == 0:
                sharpe_ratio = 0.0
            else:
                sharpe_ratio = excess_return / annualized_volatility
            
            return {
                "sharpe_ratio": float(sharpe_ratio),
                "annualized_return": float(annualized_return),
                "annualized_volatility": float(annualized_volatility)
            }
            
        except Exception as e:
            logger.error(f"Sharpe ratio calculation failed: {e}")
            return {
                "sharpe_ratio": 0.0,
                "annualized_return": 0.0,
                "annualized_volatility": 0.0
            }
    
    @staticmethod
    def calculate_max_drawdown(closes: List[float]) -> Dict[str, float]:
        """
        Calculate maximum drawdown (peak-to-trough decline)
        
        Args:
            closes: List of closing prices
        
        Returns:
            Dict with max_drawdown (as negative %), peak_value, trough_value
        """
        try:
            if len(closes) < 2:
                return {
                    "max_drawdown": 0.0,
                    "peak_value": closes[0] if closes else 0.0,
                    "trough_value": closes[0] if closes else 0.0
                }
            
            closes_arr = np.array(closes, dtype=float)
            
            # Calculate running maximum
            running_max = np.maximum.accumulate(closes_arr)
            
            # Calculate drawdown at each point
            drawdown = (closes_arr - running_max) / running_max
            
            # Find maximum drawdown
            max_drawdown = np.min(drawdown)
            
            # Find peak and trough values
            max_idx = np.argmax(running_max)
            min_idx = np.argmin(closes_arr[max_idx:]) + max_idx
            
            peak_value = running_max[max_idx]
            trough_value = closes_arr[min_idx]
            
            return {
                "max_drawdown": float(max_drawdown),
                "peak_value": float(peak_value),
                "trough_value": float(trough_value)
            }
            
        except Exception as e:
            logger.error(f"Max drawdown calculation failed: {e}")
            return {
                "max_drawdown": 0.0,
                "peak_value": 0.0,
                "trough_value": 0.0
            }
    
    @staticmethod
    def calculate_correlation(
        series_1: List[float],
        series_2: List[float]
    ) -> Dict[str, any]:
        """
        Calculate Pearson correlation between two series
        
        Args:
            series_1: First series (e.g., stock A returns)
            series_2: Second series (e.g., stock B returns)
        
        Returns:
            Dict with correlation, strength, interpretation
        """
        try:
            if len(series_1) != len(series_2) or len(series_1) < 3:
                return {
                    "correlation": 0.0,
                    "strength": CorrelationType.VERY_WEAK.value,
                    "interpretation": "Insufficient data"
                }
            
            series1_arr = np.array(series_1, dtype=float)
            series2_arr = np.array(series_2, dtype=float)
            
            # Calculate Pearson correlation
            correlation = np.corrcoef(series1_arr, series2_arr)[0, 1]
            
            # Handle NaN
            if np.isnan(correlation):
                correlation = 0.0
            
            # Classify strength
            abs_corr = abs(correlation)
            if abs_corr > 0.8:
                strength = CorrelationType.VERY_STRONG.value
            elif abs_corr > 0.6:
                strength = CorrelationType.STRONG.value
            elif abs_corr > 0.4:
                strength = CorrelationType.MODERATE.value
            elif abs_corr > 0.2:
                strength = CorrelationType.WEAK.value
            else:
                strength = CorrelationType.VERY_WEAK.value
            
            # Interpretation
            if correlation > 0:
                direction = "positive"
            elif correlation < 0:
                direction = "negative"
            else:
                direction = "no"
            
            interpretation = f"{direction.capitalize()} {strength} correlation ({correlation:.3f})"
            
            return {
                "correlation": float(correlation),
                "strength": strength,
                "interpretation": interpretation
            }
            
        except Exception as e:
            logger.error(f"Correlation calculation failed: {e}")
            return {
                "correlation": 0.0,
                "strength": CorrelationType.VERY_WEAK.value,
                "interpretation": f"Calculation failed: {str(e)}"
            }
    
    @staticmethod
    def calculate_probability_score(
        historical_pattern_matches: int,
        historical_pattern_wins: int,
        current_signal_strength: float,
        sample_size_confidence: float
    ) -> Dict[str, float]:
        """
        Calculate probability score for upside move
        
        Args:
            historical_pattern_matches: How many times pattern occurred historically
            historical_pattern_wins: How many resulted in upside
            current_signal_strength: Strength of current signal (0-1)
            sample_size_confidence: Confidence in sample size (0-1)
        
        Returns:
            Dict with probability_score, confidence
        """
        try:
            if historical_pattern_matches == 0:
                return {
                    "probability_score": 0.5,  # No historical data = neutral
                    "confidence": 0.0
                }
            
            # Historical win rate
            historical_win_rate = historical_pattern_wins / historical_pattern_matches
            
            # Weight: current signal + historical pattern
            # Current signal: 60%, Historical pattern: 40%
            probability_score = (
                current_signal_strength * 0.6 +
                historical_win_rate * 0.4
            )
            
            # Confidence increases with:
            # 1. More historical samples (diminishing return at 50+)
            # 2. Stronger signal
            # 3. Consistency between current and historical
            sample_confidence = min(historical_pattern_matches / 50, 1.0)
            consistency = 1.0 - abs(current_signal_strength - historical_win_rate)
            
            confidence = (
                sample_confidence * 0.5 +
                sample_size_confidence * 0.3 +
                consistency * 0.2
            )
            
            return {
                "probability_score": float(probability_score),
                "confidence": float(confidence)
            }
            
        except Exception as e:
            logger.error(f"Probability score calculation failed: {e}")
            return {
                "probability_score": 0.5,
                "confidence": 0.0
            }
    
    @staticmethod
    def calculate_expected_value(
        win_probability: float,
        average_win: float,
        average_loss: float,
        win_rate_confidence: float
    ) -> Dict[str, float]:
        """
        Calculate expected value of a trade
        
        EV = (win_probability × average_win) - ((1 - win_probability) × average_loss)
        
        Args:
            win_probability: Probability of winning (0-1)
            average_win: Average profit when winning (as decimal, e.g., 0.03 = 3%)
            average_loss: Average loss when losing (as decimal, e.g., 0.02 = 2%)
            win_rate_confidence: Confidence in win rate (0-1)
        
        Returns:
            Dict with expected_value, ev_classification, recommendation
        """
        try:
            win_prob = max(0.0, min(1.0, win_probability))
            
            # Calculate EV
            expected_value = (
                win_prob * average_win -
                (1 - win_prob) * average_loss
            )
            
            # Classify
            if expected_value > 0.02:  # >2% EV is excellent
                ev_classification = "excellent"
                recommendation = "strong_buy"
            elif expected_value > 0.01:  # >1% EV is good
                ev_classification = "good"
                recommendation = "buy"
            elif expected_value > 0.0:  # >0% EV is positive
                ev_classification = "positive"
                recommendation = "slight_buy"
            elif expected_value > -0.01:  # >-1% EV is acceptable
                ev_classification = "acceptable"
                recommendation = "hold"
            else:
                ev_classification = "negative"
                recommendation = "avoid"
            
            # Adjust confidence by win_rate_confidence
            adjusted_ev = expected_value * win_rate_confidence
            
            return {
                "expected_value": float(expected_value),
                "adjusted_expected_value": float(adjusted_ev),
                "ev_classification": ev_classification,
                "recommendation": recommendation,
                "profit_factor": float((average_win * win_prob) / (average_loss * (1 - win_prob))) if average_loss > 0 else 0.0
            }
            
        except Exception as e:
            logger.error(f"Expected value calculation failed: {e}")
            return {
                "expected_value": 0.0,
                "adjusted_expected_value": 0.0,
                "ev_classification": "unknown",
                "recommendation": "investigate",
                "profit_factor": 0.0
            }
    
    @staticmethod
    def calculate_trend_strength(
        closes: List[float],
        period: int = 20
    ) -> Dict[str, float]:
        """
        Calculate trend strength (0-1 scale)
        
        Uses R-squared of linear regression to measure trend strength
        
        Args:
            closes: List of closing prices
            period: Period to analyze
        
        Returns:
            Dict with trend_strength, r_squared, slope
        """
        try:
            if len(closes) < period:
                period = len(closes)
            
            closes_arr = np.array(closes[-period:], dtype=float)
            x = np.arange(len(closes_arr))
            
            # Linear regression
            coefficients = np.polyfit(x, closes_arr, 1)
            slope = coefficients[0]
            intercept = coefficients[1]
            
            # Fitted values
            fitted = slope * x + intercept
            
            # R-squared
            ss_res = np.sum((closes_arr - fitted) ** 2)
            ss_tot = np.sum((closes_arr - np.mean(closes_arr)) ** 2)
            
            if ss_tot == 0:
                r_squared = 0.0
            else:
                r_squared = 1 - (ss_res / ss_tot)
            
            # Trend strength (R-squared, 0-1)
            trend_strength = max(0.0, min(1.0, r_squared))
            
            return {
                "trend_strength": float(trend_strength),
                "r_squared": float(r_squared),
                "slope": float(slope)
            }
            
        except Exception as e:
            logger.error(f"Trend strength calculation failed: {e}")
            return {
                "trend_strength": 0.0,
                "r_squared": 0.0,
                "slope": 0.0
            }
    
    @staticmethod
    def simulate_scenarios(
        current_price: float,
        probability_up: float,
        expected_move_up: float,
        expected_move_down: float,
        volatility: float,
        simulations: int = 1000
    ) -> Dict[str, any]:
        """
        Monte Carlo simulation of price scenarios
        
        Args:
            current_price: Current price
            probability_up: Probability of upside move
            expected_move_up: Expected % move if up
            expected_move_down: Expected % move if down
            volatility: Price volatility (annual)
            simulations: Number of simulations
        
        Returns:
            Dict with median_price, percentiles, upside_capture, downside_capture
        """
        try:
            # Simple scenario simulation
            scenarios = []
            
            for _ in range(simulations):
                if np.random.random() < probability_up:
                    move = expected_move_up
                else:
                    move = -expected_move_down
                
                # Add volatility noise
                noise = np.random.normal(0, volatility)
                final_price = current_price * (1 + move + noise)
                scenarios.append(final_price)
            
            scenarios_arr = np.array(scenarios)
            
            return {
                "median_price": float(np.median(scenarios_arr)),
                "mean_price": float(np.mean(scenarios_arr)),
                "p25": float(np.percentile(scenarios_arr, 25)),
                "p75": float(np.percentile(scenarios_arr, 75)),
                "p10": float(np.percentile(scenarios_arr, 10)),
                "p90": float(np.percentile(scenarios_arr, 90)),
                "min_price": float(np.min(scenarios_arr)),
                "max_price": float(np.max(scenarios_arr)),
                "upside_capture": float((np.percentile(scenarios_arr, 75) - current_price) / current_price),
                "downside_capture": float((current_price - np.percentile(scenarios_arr, 25)) / current_price)
            }
            
        except Exception as e:
            logger.error(f"Scenario simulation failed: {e}")
            return {
                "median_price": current_price,
                "mean_price": current_price,
                "p25": current_price,
                "p75": current_price,
                "p10": current_price,
                "p90": current_price,
                "min_price": current_price,
                "max_price": current_price,
                "upside_capture": 0.0,
                "downside_capture": 0.0
            }
    
    @staticmethod
    def detect_anomaly(
        recent_value: float,
        historical_values: List[float],
        std_dev_threshold: float = 2.0
    ) -> Dict[str, any]:
        """
        Detect statistical anomalies (outliers)
        
        Args:
            recent_value: Current value to test
            historical_values: Historical values for comparison
            std_dev_threshold: Threshold in standard deviations (default 2.0 = 95%)
        
        Returns:
            Dict with is_anomaly, z_score, severity
        """
        try:
            if len(historical_values) < 2:
                return {
                    "is_anomaly": False,
                    "z_score": 0.0,
                    "severity": "none",
                    "interpretation": "Insufficient historical data"
                }
            
            hist_arr = np.array(historical_values, dtype=float)
            
            mean = np.mean(hist_arr)
            std = np.std(hist_arr)
            
            if std == 0:
                return {
                    "is_anomaly": False,
                    "z_score": 0.0,
                    "severity": "none",
                    "interpretation": "No variation in historical data"
                }
            
            # Calculate z-score
            z_score = (recent_value - mean) / std
            
            # Determine severity
            abs_z = abs(z_score)
            if abs_z > std_dev_threshold * 2:
                severity = "extreme"
                is_anomaly = True
            elif abs_z > std_dev_threshold:
                severity = "high"
                is_anomaly = True
            elif abs_z > 1.0:
                severity = "moderate"
                is_anomaly = False
            else:
                severity = "none"
                is_anomaly = False
            
            interpretation = f"Value is {abs_z:.2f} standard deviations from mean"
            
            return {
                "is_anomaly": is_anomaly,
                "z_score": float(z_score),
                "severity": severity,
                "interpretation": interpretation,
                "mean": float(mean),
                "std_dev": float(std)
            }
            
        except Exception as e:
            logger.error(f"Anomaly detection failed: {e}")
            return {
                "is_anomaly": False,
                "z_score": 0.0,
                "severity": "unknown",
                "interpretation": f"Analysis failed: {str(e)}"
            }
